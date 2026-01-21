"""
Content type detection service.

_Requirements: 2.1, 2.2, 2.3, 2.4_
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ContentType:
    type: str
    confidence: float
    matched_keywords: List[str]


class ContentTypeDetector:
    """
    Detect whether a prompt is searching for songs or sound effects.
    """

    def __init__(self, keywords_config_path: str = "backend/config/detection_keywords.json"):
        config_path = Path(keywords_config_path)
        if not config_path.is_absolute():
            config_path = Path.cwd() / config_path

        if not config_path.exists():
            raise FileNotFoundError(f"Keywords config not found: {config_path}")

        data = json.loads(config_path.read_text(encoding="utf-8"))
        self.music_keywords = [kw.lower() for kw in data.get("music_keywords", [])]
        self.sfx_keywords = [kw.lower() for kw in data.get("sfx_keywords", [])]

        logger.info(
            "ContentTypeDetector initialized with %d music keywords and %d sfx keywords",
            len(self.music_keywords),
            len(self.sfx_keywords),
        )

    def detect(self, english_text: str) -> ContentType:
        """
        Determine content type from English text.

        _Requirements: 2.2, 2.3, 2.4_
        """
        text = english_text.lower()
        music_matches = [kw for kw in self.music_keywords if kw in text]
        sfx_matches = [kw for kw in self.sfx_keywords if kw in text]

        music_count = len(music_matches)
        sfx_count = len(sfx_matches)

        if sfx_count > music_count:
            detected_type = "sfx"
        else:
            detected_type = "song"

        confidence = self._calculate_confidence(music_count, sfx_count)
        matched_keywords = sorted(set(music_matches + sfx_matches))

        return ContentType(
            type=detected_type,
            confidence=confidence,
            matched_keywords=matched_keywords,
        )

    def _calculate_confidence(self, music_count: int, sfx_count: int) -> float:
        total = music_count + sfx_count
        if total == 0:
            return 0.0
        return max(music_count, sfx_count) / total
