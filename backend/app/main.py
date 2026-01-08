"""
FastAPI application entry point.

This module defines the main FastAPI application with:
- Lifespan events for startup/shutdown
- CORS middleware configuration
- Route registration
- Static file serving setup
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events for the FastAPI application.
    This includes model initialization and cleanup.
    """
    # Startup: Initialize services
    # TODO: Initialize CLAP model and other services
    print("Application startup: Initializing services...")

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
