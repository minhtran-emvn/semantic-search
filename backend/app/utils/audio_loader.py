"""
Audio file discovery utilities.

Provides helpers for locating audio files in a directory tree.
"""

import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = [".wav", ".mp3", ".flac", ".ogg", ".m4a"]


def scan_audio_files(directory: Path) -> List[Path]:
    """
    Recursively scan a directory for supported audio files.

    Args:
        directory: Root directory to scan.

    Returns:
        List of absolute Paths to audio files.
    """
    directory = directory.expanduser()
    if not directory.is_absolute():
        directory = directory.resolve()

    audio_files = [
        path.resolve()
        for path in directory.glob("**/*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_FORMATS
    ]

    logger.info("Found %d audio file(s) under %s", len(audio_files), directory)
    return audio_files
