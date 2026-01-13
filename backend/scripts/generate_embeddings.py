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
from app.utils.audio_loader import scan_audio_files

logger = logging.getLogger(__name__)

BATCH_SIZE = 16
PROGRESS_INTERVAL = 10


def _batch_paths(paths: List[Path], batch_size: int) -> List[List[Path]]:
    return [paths[index:index + batch_size] for index in range(0, len(paths), batch_size)]


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
        required=True,
        type=Path,
        help="Directory to write embeddings output.",
    )
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "mps", "cuda"],
        help="Device override for CLAP model (default: auto).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    audio_files = scan_audio_files(args.audio_dir)
    if not audio_files:
        logger.warning("No audio files found in %s", args.audio_dir)
        return

    device_override = None if args.device == "auto" else args.device
    logger.info("Embedding run config: device=%s, batch_size=%d", device_override or "auto", BATCH_SIZE)
    clap_service = CLAPService(device=device_override)
    clap_service.load_model()

    embeddings_batches = []
    successful_paths = []
    failed_paths = []
    processed_count = 0
    total_files = len(audio_files)

    for batch in _batch_paths(audio_files, BATCH_SIZE):
        batch_paths = [str(path) for path in batch]
        try:
            embeddings = clap_service.get_audio_embeddings(batch_paths)
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
                    embeddings = clap_service.get_audio_embeddings([str(path)])
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
    file_paths = [str(path) for path in successful_paths]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    embeddings_path = args.output_dir / "embeddings.npz"
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
    metadata_path = args.output_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file)
    logger.info(
        "Saved metadata to %s (%d bytes)",
        metadata_path,
        metadata_path.stat().st_size,
    )

    index = faiss.IndexFlatIP(embeddings_array.shape[1])
    if embeddings_array.size:
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        normalized = embeddings_array / (norms + 1e-8)
        index.add(normalized.astype("float32"))
    index_path = args.output_dir / "index.faiss"
    faiss.write_index(index, str(index_path))
    logger.info(
        "Saved FAISS index to %s (%d bytes)",
        index_path,
        index_path.stat().st_size,
    )

    logger.info(
        "Embedding generation summary: total=%d, successful=%d, failed=%d, output=%s",
        total_files,
        len(successful_paths),
        len(failed_paths),
        args.output_dir,
    )


if __name__ == "__main__":
    main()
