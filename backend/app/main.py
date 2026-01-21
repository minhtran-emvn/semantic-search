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
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import settings
from app.core.clap_service import CLAPService
from app.core.content_type_detector import ContentTypeDetector
from app.core.query_processor import QueryProcessor
from app.core.search_service import SearchService
from app.core.translation_service import TranslationService

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
        clap_service.load_model(
            enable_fusion=settings.CLAP_ENABLE_FUSION,
            checkpoint_path=settings.CLAP_CHECKPOINT_PATH or None,
        )

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

        if settings.MUSIC_MODEL_ENABLED:
            try:
                clap_service.load_music_model()
                logger.info("Music CLAP model loaded successfully")
            except Exception:
                logger.exception("Failed to load music CLAP model")

            if not search_service.load_music_index():
                logger.warning("Music index not loaded; music search may be unavailable")
        else:
            logger.info("Music CLAP model disabled; using general audio model only.")

        try:
            translation_service = TranslationService(
                provider=settings.TRANSLATION_SERVICE_PROVIDER,
                api_key=settings.TRANSLATION_API_KEY or "",
                api_url=settings.TRANSLATION_API_URL,
                allowed_langs=settings.TRANSLATION_ALLOWED_LANGS,
            )
            keywords_path = Path(__file__).resolve().parents[1] / "config" / "detection_keywords.json"
            content_type_detector = ContentTypeDetector(
                keywords_config_path=str(keywords_path)
            )
            query_processor = QueryProcessor(
                enable_synonyms=True,
                enable_templates=True,
            )
        except Exception:
            logger.exception("Failed to initialize translation or detection services")
            raise

        app.state.clap_service = clap_service
        app.state.search_service = search_service
        app.state.translation_service = translation_service
        app.state.content_type_detector = content_type_detector
        app.state.query_processor = query_processor

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
