"""
Search service for semantic audio search using FAISS.

This module provides a service for managing FAISS index operations and metadata
for semantic similarity search of audio embeddings.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import faiss
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from a semantic audio search query."""
    filename: str
    similarity: float
    audio_url: str


class SearchService:
    """
    Service for managing FAISS index and search operations.

    Handles loading pre-computed embeddings and metadata, and provides methods
    for performing semantic similarity search on audio files.
    """

    def __init__(self, embeddings_dir: Path):
        """
        Initialize search service with embeddings directory.

        Automatically loads the FAISS index from disk if index.faiss exists.

        Args:
            embeddings_dir: Path to directory containing embeddings, index, and metadata files
        """
        self.embeddings_dir: Path = embeddings_dir
        self.sfx_embeddings_dir: Path = self._resolve_sfx_dir(embeddings_dir)
        self.music_embeddings_dir: Path = settings.MUSIC_EMBEDDINGS_DIR
        self.index: Optional[faiss.Index] = None
        self.metadata: Dict = {}
        self.music_index: Optional[faiss.Index] = None
        self.music_metadata: Dict = {}
        self.musicness_scores: Optional[np.ndarray] = None

        logger.info(
            "Search service initialized with embeddings directory: %s (sfx=%s, music=%s)",
            embeddings_dir,
            self.sfx_embeddings_dir,
            self.music_embeddings_dir,
        )

        # Check if index.faiss exists and load it automatically
        index_path = self.sfx_embeddings_dir / "index.faiss"
        if index_path.exists():
            try:
                self.load_index(index_path)
            except Exception as e:
                logger.warning(
                    f"Failed to load existing index from {index_path}: {str(e)}. "
                    "Index will need to be rebuilt."
                )

        self._load_content_scores()

    def _resolve_sfx_dir(self, embeddings_dir: Path) -> Path:
        sfx_dir = embeddings_dir / "sfx"
        return sfx_dir if sfx_dir.exists() else embeddings_dir

    def _load_content_scores(self) -> None:
        scores_path = self.sfx_embeddings_dir / "content_scores.npz"
        if not scores_path.exists():
            return

        try:
            npz_data = np.load(scores_path)
            if "musicness" not in npz_data:
                logger.warning("content_scores.npz missing 'musicness' array")
                return
            self.musicness_scores = npz_data["musicness"].astype("float32")
            logger.info(
                "Loaded content scores from %s (entries=%d)",
                scores_path,
                self.musicness_scores.shape[0],
            )
        except Exception as exc:
            logger.warning("Failed to load content scores: %s", exc, exc_info=True)
            self.musicness_scores = None

    def _load_metadata(self) -> Dict:
        """
        Load metadata from metadata.json file.

        The metadata file contains information about indexed audio files including
        filenames and file paths.

        Returns:
            Dictionary containing metadata with keys 'filenames' and 'file_paths'

        Raises:
            FileNotFoundError: If metadata.json does not exist
            json.JSONDecodeError: If metadata.json is not valid JSON
        """
        metadata_path = self.sfx_embeddings_dir / "metadata.json"

        if not metadata_path.exists():
            error_msg = f"Metadata file not found: {metadata_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(f"Loading metadata from {metadata_path}")

        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            logger.info(
                f"Metadata loaded successfully - "
                f"files: {len(metadata.get('filenames', []))}"
            )

            return metadata

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in metadata file {metadata_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

    def _load_embeddings(self) -> np.ndarray:
        """
        Load embeddings from embeddings.npz file.

        The embeddings file contains pre-computed audio embeddings stored as a
        compressed numpy array.

        Returns:
            2D numpy array of shape (N, 512) containing audio embeddings,
            where N is the number of indexed audio files

        Raises:
            FileNotFoundError: If embeddings.npz does not exist
            KeyError: If 'embeddings' key is not found in the npz file
        """
        embeddings_path = self.sfx_embeddings_dir / "embeddings.npz"

        if not embeddings_path.exists():
            error_msg = f"Embeddings file not found: {embeddings_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(f"Loading embeddings from {embeddings_path}")

        try:
            # Load the npz file
            npz_data = np.load(embeddings_path)

            # Extract the embeddings array
            if "embeddings" not in npz_data:
                error_msg = f"'embeddings' key not found in {embeddings_path}"
                logger.error(error_msg)
                raise KeyError(error_msg)

            embeddings = npz_data["embeddings"]

            logger.info(
                f"Embeddings loaded successfully - "
                f"shape: {embeddings.shape}, dtype: {embeddings.dtype}"
            )

            return embeddings

        except Exception as e:
            logger.error(
                f"Failed to load embeddings from {embeddings_path}: {str(e)}",
                exc_info=True,
            )
            raise

    def build_index(self, embeddings: np.ndarray) -> None:
        """
        Build FAISS index from pre-computed embeddings.

        Creates an IndexFlatIP (inner product) index for fast cosine similarity search.
        Embeddings are normalized to unit length before indexing to enable cosine
        similarity computation via dot product.

        Args:
            embeddings: 2D numpy array of shape (N, 512) containing audio embeddings

        Raises:
            ValueError: If embeddings have incorrect shape or dtype
        """
        # Validate embeddings shape
        if embeddings.ndim != 2:
            error_msg = f"Embeddings must be 2D array, got {embeddings.ndim}D"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if embeddings.shape[1] != 512:
            error_msg = f"Embeddings must have dimension 512, got {embeddings.shape[1]}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        num_vectors = embeddings.shape[0]
        logger.info(f"Building FAISS index for {num_vectors} vectors with dimension 512")

        # Normalize embeddings to unit length for cosine similarity
        # L2 normalization: v_normalized = v / ||v||
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized_embeddings = embeddings / (norms + 1e-8)  # Add epsilon to avoid division by zero

        logger.info("Embeddings normalized to unit length")

        # Create FAISS IndexFlatIP for inner product search
        # With normalized vectors, inner product = cosine similarity
        self.index = faiss.IndexFlatIP(512)

        # Convert to float32 as required by FAISS
        embeddings_float32 = normalized_embeddings.astype('float32')

        # Add embeddings to index
        self.index.add(embeddings_float32)

        logger.info(
            f"FAISS index built successfully - "
            f"total vectors: {self.index.ntotal}, "
            f"dimension: {self.index.d}"
        )

    def save_index(self, path: Path) -> None:
        """
        Save FAISS index to disk.

        Persists the current FAISS index to a file for later loading,
        avoiding the need to rebuild the index on application restart.

        Args:
            path: Path where the index file should be saved

        Raises:
            RuntimeError: If FAISS index has not been built yet
            IOError: If index file cannot be written
        """
        if self.index is None:
            error_msg = "Cannot save index: FAISS index has not been built yet."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        logger.info(f"Saving FAISS index to {path}")

        try:
            # Create parent directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write index to disk
            faiss.write_index(self.index, str(path))

            logger.info(
                f"FAISS index saved successfully - "
                f"file: {path}, "
                f"size: {path.stat().st_size} bytes"
            )

        except Exception as e:
            error_msg = f"Failed to save FAISS index to {path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise IOError(error_msg) from e

    def load_index(self, path: Path) -> None:
        """
        Load FAISS index from disk.

        Loads a previously saved FAISS index from a file, restoring the
        search capability without needing to rebuild from embeddings.

        Args:
            path: Path to the saved index file

        Raises:
            FileNotFoundError: If index file does not exist
            IOError: If index file cannot be read or is corrupted
        """
        if not path.exists():
            error_msg = f"Index file not found: {path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(f"Loading FAISS index from {path}")

        try:
            # Read index from disk
            self.index = faiss.read_index(str(path))

            logger.info(
                f"FAISS index loaded successfully - "
                f"total vectors: {self.index.ntotal}, "
                f"dimension: {self.index.d}"
            )

        except Exception as e:
            error_msg = f"Failed to load FAISS index from {path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            # Reset index to None on failure
            self.index = None
            raise IOError(error_msg) from e

    def build_music_index(self, embeddings: np.ndarray, metadata: Dict) -> None:
        """
        Build FAISS index for music embeddings.

        _Requirements: 3.4_
        """
        self._build_index_for_embeddings(embeddings, is_music=True)
        self.music_metadata = metadata

    def load_music_index(self) -> bool:
        """
        Load music FAISS index from disk.

        _Requirements: 3.4_
        """
        index_path = self.music_embeddings_dir / "index.faiss"
        metadata_path = self.music_embeddings_dir / "metadata.json"

        if not index_path.exists() or not metadata_path.exists():
            logger.warning("Music index or metadata not found in %s", self.music_embeddings_dir)
            return False

        try:
            self.music_index = faiss.read_index(str(index_path))
            with metadata_path.open("r", encoding="utf-8") as file_handle:
                self.music_metadata = json.load(file_handle)
            return True
        except Exception as exc:
            logger.error("Failed to load music index: %s", exc, exc_info=True)
            self.music_index = None
            self.music_metadata = {}
            return False

    def search_by_content_type(
        self,
        query_embedding: np.ndarray,
        content_type: str,
        k: int = 20,
    ) -> List[SearchResult]:
        """
        Search appropriate index based on content type.

        _Requirements: 3.4, 3.5, 5.3_
        """
        normalized_type = content_type.lower()
        musicness_scores = None
        rerank_weight = 0.0

        if normalized_type == "song":
            if self.music_index is None:
                logger.warning(
                    "Music index unavailable; falling back to general audio index."
                )
                index = self.index
                metadata = self.metadata
                musicness_scores = self.musicness_scores
                if settings.CONTENT_RERANK_ENABLED:
                    rerank_weight = settings.CONTENT_RERANK_WEIGHT
            else:
                index = self.music_index
                metadata = self.music_metadata
        else:
            index = self.index
            metadata = self.metadata
            musicness_scores = self.musicness_scores
            if settings.CONTENT_RERANK_ENABLED:
                rerank_weight = settings.CONTENT_RERANK_WEIGHT

        results = self._search_index(
            index,
            metadata,
            query_embedding,
            k,
            content_type=normalized_type,
            musicness_scores=musicness_scores,
            rerank_weight=rerank_weight,
        )
        if rerank_weight <= 0.0 or musicness_scores is None or normalized_type not in {"song", "sfx"}:
            results.sort(key=lambda result: result.similarity, reverse=True)
        return results

    def _build_index_for_embeddings(self, embeddings: np.ndarray, is_music: bool) -> None:
        if embeddings.ndim != 2:
            error_msg = f"Embeddings must be 2D array, got {embeddings.ndim}D"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if embeddings.shape[1] != 512:
            error_msg = f"Embeddings must have dimension 512, got {embeddings.shape[1]}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        num_vectors = embeddings.shape[0]
        logger.info(
            "Building FAISS index for %d vectors with dimension 512 (music=%s)",
            num_vectors,
            is_music,
        )

        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized_embeddings = embeddings / (norms + 1e-8)

        index = faiss.IndexFlatIP(512)
        embeddings_float32 = normalized_embeddings.astype("float32")
        index.add(embeddings_float32)

        if is_music:
            self.music_index = index
        else:
            self.index = index

    def _search_index(
        self,
        index: Optional[faiss.Index],
        metadata: Dict,
        query_embedding: np.ndarray,
        k: int,
        content_type: Optional[str] = None,
        musicness_scores: Optional[np.ndarray] = None,
        rerank_weight: float = 0.0,
    ) -> List[SearchResult]:
        if index is None:
            error_msg = "FAISS index has not been built. Call build_index() first."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        if query_embedding.ndim != 1:
            error_msg = f"Query embedding must be 1D array, got {query_embedding.ndim}D"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if query_embedding.shape[0] != 512:
            error_msg = f"Query embedding must have dimension 512, got {query_embedding.shape[0]}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if index.ntotal == 0:
            logger.warning("FAISS index is empty; returning no results")
            return []

        if k > index.ntotal:
            logger.info(
                "Requested k=%d exceeds index size=%d; reducing k",
                k,
                index.ntotal,
            )
            k = index.ntotal

        norm = np.linalg.norm(query_embedding)
        normalized_query = query_embedding / (norm + 1e-8)
        query_array = normalized_query.reshape(1, -1).astype("float32")

        distances, indices = index.search(query_array, k)
        distances = distances[0]
        indices = indices[0]

        results = []
        rerank_candidates = []
        filenames = metadata.get("filenames", [])
        file_paths = metadata.get("file_paths", [])
        can_rerank = (
            rerank_weight > 0.0
            and musicness_scores is not None
            and len(musicness_scores) >= len(filenames)
            and content_type in {"song", "sfx"}
        )

        for idx, distance in zip(indices, distances):
            if idx < 0 or idx >= len(filenames):
                logger.warning("Invalid index %d returned from FAISS search", idx)
                continue

            filename = filenames[idx]
            file_path = file_paths[idx] if idx < len(file_paths) else filename
            audio_url = self._build_audio_url(file_path, filename)

            similarity = (float(distance) + 1.0) / 2.0
            similarity = max(0.0, min(1.0, similarity))

            result = SearchResult(
                filename=filename,
                similarity=similarity,
                audio_url=audio_url,
            )
            results.append(result)

            if can_rerank:
                musicness = float(musicness_scores[idx])
                musicness = max(0.0, min(1.0, musicness))
                if content_type == "song":
                    target_score = musicness
                else:
                    target_score = 1.0 - musicness
                combined_score = (1.0 - rerank_weight) * similarity + rerank_weight * target_score
                rerank_candidates.append((combined_score, result))

        if can_rerank and rerank_candidates:
            rerank_candidates.sort(key=lambda item: item[0], reverse=True)
            results = [result for _, result in rerank_candidates]

        return results

    def _build_audio_url(self, file_path: str, filename: str) -> str:
        try:
            path_obj = Path(file_path)
            if not path_obj.is_absolute():
                return f"/audio/{path_obj.as_posix()}"

            resolved_path = path_obj.resolve()
            relative_path = resolved_path.relative_to(settings.AUDIO_DIR)
            return f"/audio/{relative_path.as_posix()}"
        except Exception:
            return f"/audio/{filename}"

    def search(self, query_embedding: np.ndarray, k: int = 20) -> List[SearchResult]:
        """
        Perform semantic similarity search on audio embeddings.

        Searches the FAISS index for the k most similar audio files to the query
        embedding. Results are ranked by cosine similarity score (descending).

        Args:
            query_embedding: 1D numpy array of shape (512,) containing query embedding
            k: Number of top results to return (default: 20)

        Returns:
            List of SearchResult objects sorted by similarity (descending)

        Raises:
            RuntimeError: If FAISS index has not been built yet
            ValueError: If query_embedding has incorrect shape
        """
        results = self._search_index(self.index, self.metadata, query_embedding, k)

        logger.info(
            "Returning %d results - %s",
            len(results),
            f"top similarity: {results[0].similarity:.4f}" if results else "no results",
        )

        return results
