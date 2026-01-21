"""
Application configuration using Pydantic settings.

This module defines the configuration settings for the semantic audio search application.
All settings can be overridden via environment variables.
"""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    All settings can be configured via environment variables.
    The .env file is automatically loaded if present.
    """

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        env_ignore_empty=True
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

    CLAP_ENABLE_FUSION: bool = Field(
        default=False,
        description="Enable CLAP fusion model for variable-length audio."
    )

    CLAP_CHECKPOINT_PATH: Optional[str] = Field(
        default=None,
        description="Optional checkpoint path override for the general CLAP model."
    )

    MUSIC_MODEL_ENABLED: bool = Field(
        default=True,
        description="Whether to initialize the music-specific CLAP model."
    )

    CONTENT_RERANK_ENABLED: bool = Field(
        default=True,
        description="Enable content-type reranking for mixed audio datasets."
    )

    CONTENT_RERANK_WEIGHT: float = Field(
        default=0.35,
        description="Weight for content-type reranking (0.0-1.0).",
        ge=0.0,
        le=1.0,
    )

    MUSIC_CHECKPOINT_PATH: str = Field(
        default="music_audioset_epoch_15_esc_90.14.pt",
        description="Checkpoint path for music-optimized CLAP model"
    )

    MUSIC_EMBEDDINGS_DIR: Path = Field(
        default=Path("data/embeddings/music"),
        description="Directory to store music embeddings"
    )

    # Translation service configuration
    TRANSLATION_SERVICE_PROVIDER: str = Field(
        default="googletrans",
        description="Translation provider: 'google', 'googletrans', or 'deepl'"
    )

    TRANSLATION_API_KEY: Optional[str] = Field(
        default=None,
        description="API key for translation provider"
    )

    TRANSLATION_API_URL: Optional[str] = Field(
        default=None,
        description="Custom translation API URL for self-hosted providers"
    )

    TRANSLATION_ALLOWED_LANGS: List[str] = Field(
        default=["vi"],
        description="Allowed source languages for translation (default: Vietnamese only)"
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
        default=10,
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

        if not self.MUSIC_EMBEDDINGS_DIR.is_absolute():
            self.MUSIC_EMBEDDINGS_DIR = Path(os.getcwd()) / self.MUSIC_EMBEDDINGS_DIR

        self.MUSIC_EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
