"""
CLI tool for generating audio embeddings in batches.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import List

import faiss
import numpy as np

from app.core.clap_service import CLAPService
from app.core.config import settings
from app.utils.audio_loader import scan_audio_files

logger = logging.getLogger(__name__)

BATCH_SIZE = 16
PROGRESS_INTERVAL = 10
MUSIC_PROMPTS = [
    "music track",
    "song with vocals",
    "instrumental music",
    "melody",
]
SFX_PROMPTS = [
    "sound effect",
    "ambient noise",
    "sound of something",
    "fx sound",
]


def _batch_paths(paths: List[Path], batch_size: int) -> List[List[Path]]:
    return [paths[index:index + batch_size] for index in range(0, len(paths), batch_size)]


def _normalize_rows(array: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(array, axis=1, keepdims=True)
    return array / (norms + 1e-8)


def _compute_musicness_scores(
    normalized_embeddings: np.ndarray,
    model,
) -> np.ndarray:
    prompts = MUSIC_PROMPTS + SFX_PROMPTS
    text_embeddings = model.get_text_embedding(prompts, use_tensor=False)
    text_embeddings = _normalize_rows(text_embeddings)

    music_vector = text_embeddings[: len(MUSIC_PROMPTS)].mean(axis=0)
    sfx_vector = text_embeddings[len(MUSIC_PROMPTS):].mean(axis=0)

    music_vector = music_vector / (np.linalg.norm(music_vector) + 1e-8)
    sfx_vector = sfx_vector / (np.linalg.norm(sfx_vector) + 1e-8)

    music_scores = normalized_embeddings @ music_vector
    sfx_scores = normalized_embeddings @ sfx_vector
    diff = music_scores - sfx_scores
    musicness = (diff + 2.0) / 4.0
    return np.clip(musicness, 0.0, 1.0).astype("float32")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CLAP audio embeddings.")
    parser.add_argument(
        "--audio-dir",
        required=True,
        type=Path,
        help="Directory containing audio files to embed.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to write embeddings output.",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        help="Optional checkpoint path override.",
    )
    parser.add_argument(
        "--content-type",
        default="sfx",
        choices=["song", "sfx"],
        help="Content type for embeddings (default: sfx).",
    )
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "mps", "cuda"],
        help="Device override for CLAP model (default: auto).",
    )
    parser.add_argument(
        "--enable-fusion",
        default=settings.CLAP_ENABLE_FUSION,
        action=argparse.BooleanOptionalAction,
        help="Enable fusion model (default: CLAP_ENABLE_FUSION).",
    )
    parser.add_argument(
        "--compute-musicness",
        default=None,
        action=argparse.BooleanOptionalAction,
        help="Compute musicness scores for mixed datasets (default: true for sfx).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    audio_root = args.audio_dir.expanduser().resolve()
    audio_files = scan_audio_files(args.audio_dir)
    if not audio_files:
        logger.warning("No audio files found in %s", args.audio_dir)
        return

    device_override = None if args.device == "auto" else args.device
    clap_service = CLAPService(device=device_override)

    if args.content_type == "song":
        clap_service.load_music_model(checkpoint_path=args.checkpoint)
        active_model = clap_service.music_model
    else:
        clap_service.load_model(
            enable_fusion=args.enable_fusion,
            checkpoint_path=args.checkpoint,
        )
        active_model = clap_service.model

    if active_model is None:
        raise RuntimeError("CLAP model failed to initialize for embedding generation.")

    embeddings_batches = []
    successful_paths = []
    failed_paths = []
    processed_count = 0
    total_files = len(audio_files)

    for batch in _batch_paths(audio_files, BATCH_SIZE):
        batch_paths = [str(path) for path in batch]
        try:
            embeddings = active_model.get_audio_embedding_from_filelist(
                x=batch_paths,
                use_tensor=False,
            )
            embeddings_batches.append(embeddings)
            successful_paths.extend(batch)
            processed_count += len(batch)
            if processed_count % PROGRESS_INTERVAL == 0 or processed_count == total_files:
                logger.info("Processed %d/%d files", processed_count, total_files)
        except Exception as exc:
            logger.warning(
                "Batch embedding failed, falling back to per-file processing: %s",
                exc,
            )
            for path in batch:
                try:
                    embeddings = active_model.get_audio_embedding_from_filelist(
                        x=[str(path)],
                        use_tensor=False,
                    )
                    embeddings_batches.append(embeddings)
                    successful_paths.append(path)
                except Exception as file_exc:
                    failed_paths.append(path)
                    logger.error("Skipping file %s: %s", path, file_exc)
                finally:
                    processed_count += 1
                    if processed_count % PROGRESS_INTERVAL == 0 or processed_count == total_files:
                        logger.info("Processed %d/%d files", processed_count, total_files)

    if embeddings_batches:
        embeddings_array = np.vstack(embeddings_batches)
    else:
        logger.warning("No embeddings generated successfully; output will be empty.")
        embeddings_array = np.empty((0, 512), dtype=np.float32)

    filenames_array = np.array([path.name for path in successful_paths])
    file_paths = []
    for path in successful_paths:
        try:
            relative_path = path.resolve().relative_to(audio_root)
            file_paths.append(relative_path.as_posix())
        except Exception:
            file_paths.append(str(path))

    output_dir = args.output_dir
    if output_dir is None:
        output_dir = Path("data/embeddings") / args.content_type

    compute_musicness = args.compute_musicness
    if compute_musicness is None:
        compute_musicness = args.content_type != "song"

    output_dir.mkdir(parents=True, exist_ok=True)
    embeddings_path = output_dir / "embeddings.npz"
    np.savez_compressed(
        embeddings_path,
        embeddings=embeddings_array,
        filenames=filenames_array,
    )
    logger.info(
        "Saved embeddings to %s (%d bytes)",
        embeddings_path,
        embeddings_path.stat().st_size,
    )

    metadata = {
        "filenames": filenames_array.tolist(),
        "file_paths": file_paths,
        "metadata": {
            "num_files": len(filenames_array),
            "embedding_dim": int(embeddings_array.shape[1]) if embeddings_array.size else 0,
        },
    }
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file)
    logger.info(
        "Saved metadata to %s (%d bytes)",
        metadata_path,
        metadata_path.stat().st_size,
    )

    index = faiss.IndexFlatIP(embeddings_array.shape[1])
    normalized = embeddings_array
    if embeddings_array.size:
        normalized = _normalize_rows(embeddings_array)
        index.add(normalized.astype("float32"))
    index_path = output_dir / "index.faiss"
    faiss.write_index(index, str(index_path))
    logger.info(
        "Saved FAISS index to %s (%d bytes)",
        index_path,
        index_path.stat().st_size,
    )

    if compute_musicness and embeddings_array.size:
        musicness = _compute_musicness_scores(normalized, active_model)
        scores_path = output_dir / "content_scores.npz"
        np.savez_compressed(scores_path, musicness=musicness)
        logger.info(
            "Saved content scores to %s (%d bytes)",
            scores_path,
            scores_path.stat().st_size,
        )

    logger.info(
        "Embedding generation summary: total=%d, successful=%d, failed=%d, output=%s",
        total_files,
        len(successful_paths),
        len(failed_paths),
        output_dir,
    )


if __name__ == "__main__":
    main()
