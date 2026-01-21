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

from app.core.config import settings

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
        self.music_model: Optional[CLAP_Module] = None
        self.current_gpu_model: Optional[str] = None
        self.device: str = self._get_device(device)
        self.device_memory: float = self._check_gpu_memory()

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

    def _check_gpu_memory(self) -> float:
        """
        Detect available GPU memory in GB.

        _Requirements: 6.1_
        """
        if self.device != "cuda" or not torch.cuda.is_available():
            return 0.0

        try:
            properties = torch.cuda.get_device_properties(0)
            total_gb = properties.total_memory / (1024 ** 3)
            logger.info("Detected GPU memory: %.2f GB", total_gb)
            return total_gb
        except Exception as exc:
            logger.warning("Failed to detect GPU memory: %s", exc)
            return 0.0

    def load_model(
        self,
        enable_fusion: bool = False,
        checkpoint_path: Optional[str] = None,
    ) -> None:
        """
        Load CLAP model with automatic checkpoint download.

        Configuration:
        - Audio model: HTSAT-tiny
        - Text model: roberta
        - Enable fusion: False by default (optimized for <10 sec audio)
        - Checkpoint: CLAP default checkpoint (fusion uses 630k-audioset-fusion-best.pt)

        Args:
            enable_fusion: Whether to enable fusion mode (use True for audio >10 seconds)
            checkpoint_path: Optional checkpoint path override

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
                if checkpoint_path:
                    self.model.load_ckpt(ckpt=checkpoint_path)
                else:
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

    def load_music_model(self, checkpoint_path: Optional[str] = None) -> None:
        """
        Load music-optimized CLAP model checkpoint.

        _Requirements: 6.1, 6.2, 6.5_
        """
        max_retries = 3
        last_exception = None

        for attempt in range(1, max_retries + 1):
            try:
                load_device = self.device
                if self.device == "cuda" and self.device_memory < 4.0:
                    load_device = "cpu"

                logger.info(
                    "Loading music CLAP model (attempt %d/%d) - device: %s",
                    attempt,
                    max_retries,
                    load_device,
                )

                self.music_model = CLAP_Module(
                    device=load_device,
                    enable_fusion=False,
                    amodel="HTSAT-base",
                    tmodel="roberta",
                )

                resolved_checkpoint = checkpoint_path or settings.MUSIC_CHECKPOINT_PATH
                self.music_model.load_ckpt(ckpt=resolved_checkpoint)

                logger.info("Music CLAP model loaded successfully")
                return
            except Exception as exc:
                last_exception = exc
                logger.error(
                    "Failed to load music CLAP model (attempt %d/%d): %s",
                    attempt,
                    max_retries,
                    exc,
                    exc_info=True,
                )
                self.music_model = None

                if attempt < max_retries:
                    logger.info("Retrying music model load...")

        error_msg = (
            f"Failed to load music CLAP model after {max_retries} attempts. "
            f"Last error: {str(last_exception)}"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from last_exception

    def _swap_models_if_needed(self, target_content_type: str) -> None:
        """
        Swap CLAP models between GPU and CPU based on memory constraints.

        _Requirements: 6.1_
        """
        if self.device != "cuda":
            return

        if self.device_memory >= 4.0:
            self.current_gpu_model = target_content_type
            return

        if self.current_gpu_model == target_content_type:
            return

        if target_content_type == "song":
            active_model = self.music_model
            inactive_model = self.model
        else:
            active_model = self.model
            inactive_model = self.music_model

        self._move_model_to_device(inactive_model, "cpu")
        self._move_model_to_device(active_model, "cuda")
        self.current_gpu_model = target_content_type

    def _move_model_to_device(self, model: Optional[CLAP_Module], device: str) -> None:
        if model is None:
            return

        if hasattr(model, "model") and hasattr(model.model, "to"):
            model.model.to(device)
            return

        if hasattr(model, "to"):
            model.to(device)
            return

        logger.warning("CLAP model does not support device transfer.")

    def get_text_embedding_for_content_type(self, text: str, content_type: str) -> np.ndarray:
        """
        Generate text embedding using the model for the specified content type.

        _Requirements: 6.3, 6.4_
        """
        normalized_type = content_type.lower()
        if normalized_type not in {"song", "sfx"}:
            raise ValueError(f"Unsupported content type: {content_type}")

        selected_model = self.model
        target_type = "sfx"

        if normalized_type == "song" and self.music_model is not None:
            selected_model = self.music_model
            target_type = "song"

        if selected_model is None:
            error_msg = "CLAP model is not loaded. Call load_model() first."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        self._swap_models_if_needed(target_type)

        logger.debug(
            "Generating text embedding for content_type=%s query: %s...",
            target_type,
            text[:100],
        )

        embedding = selected_model.get_text_embedding([text], use_tensor=False)
        embedding = embedding.squeeze()

        logger.debug(
            "Text embedding generated - shape: %s, dtype: %s",
            embedding.shape,
            embedding.dtype,
        )

        return embedding

    def get_multi_text_embeddings(
        self, texts: List[str], content_type: str
    ) -> List[np.ndarray]:
        """
        Generate embeddings for multiple text prompts.

        Args:
            texts: List of text prompts to embed
            content_type: Either "song" or "sfx"

        Returns:
            List of embedding arrays, one per input text
        """
        normalized_type = content_type.lower()
        if normalized_type not in {"song", "sfx"}:
            raise ValueError(f"Unsupported content type: {content_type}")

        selected_model = self.model
        target_type = "sfx"

        if normalized_type == "song" and self.music_model is not None:
            selected_model = self.music_model
            target_type = "song"

        if selected_model is None:
            error_msg = "CLAP model is not loaded. Call load_model() first."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        self._swap_models_if_needed(target_type)

        logger.debug(
            "Generating %d text embeddings for content_type=%s",
            len(texts),
            target_type,
        )

        # Get embeddings for all texts in a single batch
        embeddings = selected_model.get_text_embedding(texts, use_tensor=False)

        # Split into list of individual embeddings
        result = [embeddings[i] for i in range(embeddings.shape[0])]

        logger.debug(
            "Generated %d embeddings - shape: %s each",
            len(result),
            result[0].shape if result else "N/A",
        )

        return result

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
