"""
FastAPI application entry point.

This module defines the main FastAPI application with:
- Lifespan events for startup/shutdown
- CORS middleware configuration
- Route registration
- Static file serving setup
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import settings
from app.core.clap_service import CLAPService
from app.core.search_service import SearchService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events for the FastAPI application.
    This includes model initialization and cleanup.
    """
    # Startup: Initialize services
    try:
        device_override = None
        if settings.CLAP_DEVICE != "auto":
            device_override = settings.CLAP_DEVICE

        clap_service = CLAPService(device=device_override)
        clap_service.load_model()

        search_service = SearchService(settings.EMBEDDINGS_DIR)

        embeddings_path = settings.EMBEDDINGS_DIR / "embeddings.npz"
        metadata_path = settings.EMBEDDINGS_DIR / "metadata.json"

        if search_service.index is None and embeddings_path.exists():
            embeddings = search_service._load_embeddings()
            search_service.build_index(embeddings)
        elif search_service.index is None:
            logger.warning("Embeddings not found at %s; search index not built", embeddings_path)

        if metadata_path.exists():
            search_service.metadata = search_service._load_metadata()
        else:
            logger.warning("Metadata not found at %s; search results may be incomplete", metadata_path)

        app.state.clap_service = clap_service
        app.state.search_service = search_service

        logger.info("Application startup: services initialized")
    except Exception:
        logger.exception("Application startup failed while initializing services")
        raise

    yield

    # Shutdown: Cleanup resources
    # TODO: Cleanup CLAP model and other services
    print("Application shutdown: Cleaning up resources...")


# Create FastAPI application instance
app = FastAPI(
    title="Semantic Audio Search",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Serve audio files for playback
app.mount(
    "/audio",
    StaticFiles(directory=str(settings.AUDIO_DIR)),
    name="audio"
)
