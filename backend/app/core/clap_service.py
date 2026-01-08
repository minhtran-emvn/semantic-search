"""
CLAP model service for audio and text embeddings.

This module provides a wrapper around the CLAP (Contrastive Language-Audio Pretraining)
model with intelligent device detection and management.
"""

import logging
from typing import List, Optional

import numpy as np
import torch
from laion_clap import CLAP_Module

logger = logging.getLogger(__name__)


class CLAPService:
    """
    Service for managing CLAP model operations.

    Handles model initialization with automatic device detection (CUDA → MPS → CPU)
    and provides methods for generating embeddings from audio and text.
    """

    def __init__(self, device: Optional[str] = None):
        """
        Initialize CLAP service with device auto-detection.

        Args:
            device: Optional device override ('cuda', 'mps', 'cpu', or None for auto-detection)
        """
        self.model: Optional[CLAP_Module] = None
        self.device: str = self._get_device(device)

        logger.info(f"CLAP service initialized with device: {self.device}")

    def _get_device(self, device_override: Optional[str] = None) -> str:
        """
        Determine the compute device for CLAP model.

        Priority: CUDA (NVIDIA GPU) → MPS (Apple Silicon GPU) → CPU

        Args:
            device_override: Optional device string to override auto-detection

        Returns:
            Device string: 'cuda', 'mps', or 'cpu'
        """
        if device_override is not None:
            logger.info(f"Using device override: {device_override}")
            return device_override

        # Check for CUDA (NVIDIA GPU)
        if torch.cuda.is_available():
            logger.info("CUDA detected - using NVIDIA GPU")
            return "cuda"

        # Check for MPS (Apple Silicon GPU)
        if torch.backends.mps.is_available():
            logger.info("MPS detected - using Apple Silicon GPU")
            return "mps"

        # Fallback to CPU
        logger.info("No GPU detected - using CPU")
        return "cpu"

    def load_model(self, enable_fusion: bool = False) -> None:
        """
        Load CLAP model with automatic checkpoint download.

        Configuration:
        - Audio model: HTSAT-tiny
        - Text model: roberta
        - Enable fusion: False by default (optimized for <10 sec audio)
        - Checkpoint: 630k-audioset-best.pt (auto-downloaded from HuggingFace)

        Args:
            enable_fusion: Whether to enable fusion mode (use True for audio >10 seconds)

        Raises:
            RuntimeError: If model initialization fails after 3 retry attempts
        """
        max_retries = 3
        last_exception = None

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    f"Loading CLAP model (attempt {attempt}/{max_retries}) - "
                    f"device: {self.device}, enable_fusion: {enable_fusion}"
                )

                # Initialize CLAP model with configuration
                self.model = CLAP_Module(
                    device=self.device,
                    enable_fusion=enable_fusion,
                    amodel="HTSAT-tiny",  # Audio model
                    tmodel="roberta",  # Text model
                )

                # Load checkpoint (auto-downloads 630k-audioset-best.pt if not present)
                logger.info("Loading checkpoint (will auto-download if not present)...")
                self.model.load_ckpt()

                logger.info("CLAP model loaded successfully")
                return

            except Exception as e:
                last_exception = e
                logger.error(
                    f"Failed to load CLAP model (attempt {attempt}/{max_retries}): {str(e)}",
                    exc_info=True,
                )

                # Clean up failed model instance
                self.model = None

                # Don't retry if this is the last attempt
                if attempt < max_retries:
                    logger.info(f"Retrying model load...")

        # All retries exhausted
        error_msg = (
            f"Failed to load CLAP model after {max_retries} attempts. "
            f"Last error: {str(last_exception)}"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from last_exception

    def get_text_embedding(self, text: str) -> np.ndarray:
        """
        Generate 512-dimensional text embedding from natural language query.

        Uses the pre-loaded CLAP model to convert text into a normalized
        512-dimensional embedding vector suitable for semantic similarity search.

        Args:
            text: Natural language text query to embed

        Returns:
            1D numpy array of shape (512,) containing the normalized text embedding

        Raises:
            RuntimeError: If model is not loaded (call load_model() first)
        """
        if self.model is None:
            error_msg = "CLAP model is not loaded. Call load_model() first."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        logger.debug(f"Generating text embedding for query: {text[:100]}...")

        # Generate embedding using CLAP model
        # Returns shape (1, 512) - we need to flatten to (512,)
        embedding = self.model.get_text_embedding([text], use_tensor=False)

        # Flatten from (1, 512) to (512,)
        embedding = embedding.squeeze()

        logger.debug(f"Text embedding generated - shape: {embedding.shape}, dtype: {embedding.dtype}")

        return embedding

    def get_audio_embeddings(self, file_paths: List[str]) -> np.ndarray:
        """
        Generate 512-dimensional audio embeddings from audio file paths.

        Uses the pre-loaded CLAP model to convert audio files into normalized
        512-dimensional embedding vectors suitable for semantic similarity search.

        Args:
            file_paths: List of absolute paths to audio files to embed

        Returns:
            2D numpy array of shape (N, 512) containing normalized audio embeddings,
            where N is the number of successfully processed audio files

        Raises:
            RuntimeError: If model is not loaded (call load_model() first)
        """
        if self.model is None:
            error_msg = "CLAP model is not loaded. Call load_model() first."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        logger.info(f"Generating audio embeddings for {len(file_paths)} file(s)")

        try:
            # Generate embeddings using CLAP model
            # Returns shape (N, 512) where N is the number of files
            embeddings = self.model.get_audio_embedding_from_filelist(
                x=file_paths, use_tensor=False
            )

            logger.info(
                f"Audio embeddings generated - shape: {embeddings.shape}, dtype: {embeddings.dtype}"
            )

            return embeddings

        except Exception as e:
            logger.error(
                f"Failed to generate audio embeddings for {len(file_paths)} file(s): {str(e)}",
                exc_info=True,
            )
            raise
