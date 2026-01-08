"""
Application configuration using Pydantic settings.

This module defines the configuration settings for the semantic audio search application.
All settings can be overridden via environment variables.
"""

import os
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    All settings can be configured via environment variables.
    The .env file is automatically loaded if present.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Directory paths
    AUDIO_DIR: Path = Field(
        default=Path("data/audio"),
        description="Directory containing audio files for indexing"
    )

    EMBEDDINGS_DIR: Path = Field(
        default=Path("data/embeddings"),
        description="Directory to store generated embeddings"
    )

    # CLAP model configuration
    CLAP_DEVICE: str = Field(
        default="auto",
        description="Device for CLAP model: 'auto', 'cuda', or 'cpu'. Auto detects GPU availability."
    )

    # API server configuration
    API_HOST: str = Field(
        default="0.0.0.0",
        description="Host address for the API server"
    )

    API_PORT: int = Field(
        default=8000,
        description="Port for the API server"
    )

    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000", "http://localhost:5173"],
        description="Allowed CORS origins for API requests"
    )

    # Search configuration
    DEFAULT_TOP_K: int = Field(
        default=5,
        description="Default number of search results to return",
        ge=1
    )

    MAX_TOP_K: int = Field(
        default=50,
        description="Maximum number of search results allowed",
        ge=1
    )

    def __init__(self, **kwargs):
        """Initialize settings and ensure paths are absolute."""
        super().__init__(**kwargs)

        # Convert relative paths to absolute paths
        if not self.AUDIO_DIR.is_absolute():
            self.AUDIO_DIR = Path(os.getcwd()) / self.AUDIO_DIR

        if not self.EMBEDDINGS_DIR.is_absolute():
            self.EMBEDDINGS_DIR = Path(os.getcwd()) / self.EMBEDDINGS_DIR

        # Create directories if they don't exist
        self.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        self.EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
