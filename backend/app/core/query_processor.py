"""
Query processor for improving search quality through prompt templates and synonym expansion.

This module provides query enhancement functionality including:
- Prompt templates for better CLAP embedding
- Synonym expansion for common search terms
"""

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

import numpy as np

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProcessedQueryResult:
    """Result of query processing including expanded terms and prompt variants."""
    original_query: str
    expanded_query: str
    prompt_variants: List[str]
    synonyms_applied: List[str]


# Prompt templates for different content types
# These are designed to work with both descriptors and phrase queries
SONG_PROMPT_TEMPLATES = [
    "{query}",  # Original query first
    "music: {query}",
    "background music for {query}",
    "instrumental music {query}",
]

SFX_PROMPT_TEMPLATES = [
    "sound of {query}",
    "sound effect: {query}",
    "{query} audio",
    "{query} sound",
]

# Use-case to music style mappings
# Maps contextual queries to actual music characteristics
# Includes variations from Vietnamese translations
USE_CASE_MUSIC_MAPPINGS: Dict[str, str] = {
    # Award/ceremony (trao giải, lễ trao giải)
    "award ceremony": "triumphant orchestral fanfare victory celebration music",
    "awards ceremony": "triumphant orchestral fanfare victory celebration music",
    "award presentation": "triumphant orchestral fanfare victory music",
    "prize giving": "triumphant orchestral fanfare celebration music",
    "prize ceremony": "triumphant orchestral fanfare celebration music",
    "award": "triumphant orchestral fanfare celebration music",
    "awards": "triumphant orchestral fanfare celebration music",
    "ceremony": "elegant orchestral ceremonial grand music",
    "victory": "triumphant epic orchestral celebration fanfare",
    "winner": "triumphant celebration fanfare victorious music",
    "prize": "triumphant orchestral fanfare music",
    "celebration": "upbeat celebratory happy joyful festive music",
    "triumph": "triumphant epic orchestral victorious fanfare",
    "glory": "triumphant epic majestic orchestral music",

    # Automotive/car (xe, quảng cáo xe)
    "car advertisement": "energetic modern driving electronic powerful beat music",
    "car commercial": "powerful dynamic driving rock electronic energetic music",
    "car ad": "energetic modern driving electronic powerful music",
    "automobile advertisement": "energetic driving modern electronic powerful music",
    "vehicle advertisement": "dynamic driving energetic modern powerful music",
    "car": "energetic driving electronic rock powerful music",
    "automobile": "energetic driving modern electronic music",
    "vehicle": "dynamic driving energetic modern beat",
    "driving": "energetic electronic rock road trip upbeat music",

    # New Year/Holiday (năm mới, tết)
    "new year": "festive celebratory happy traditional joyful holiday music",
    "happy new year": "festive celebratory joyful traditional holiday music",
    "lunar new year": "festive traditional asian celebration joyful music",
    "spring festival": "festive traditional asian celebratory joyful music",
    "tet": "festive vietnamese traditional celebration joyful music",
    "tet holiday": "festive vietnamese traditional joyful celebration music",
    "holiday": "festive cheerful warm holiday celebration joyful music",
    "christmas": "festive warm holiday traditional christmas joyful music",
    "festival": "festive celebratory upbeat traditional joyful music",
    "festive": "festive celebratory joyful upbeat happy music",

    # Corporate/Business
    "corporate": "professional inspiring motivational confident business music",
    "business": "professional corporate inspiring confident modern music",
    "presentation": "professional confident corporate inspiring modern music",
    "technology": "modern electronic futuristic innovative tech inspiring music",
    "tech": "modern electronic digital futuristic innovative music",
    "startup": "energetic modern inspiring innovative tech upbeat music",
    "advertisement": "catchy upbeat modern energetic commercial music",
    "commercial": "catchy upbeat modern energetic professional music",
    "advertising": "catchy modern energetic upbeat commercial music",

    # Emotional contexts
    "wedding": "romantic elegant beautiful emotional tender love music",
    "funeral": "sad somber emotional melancholic peaceful gentle music",
    "romantic": "romantic beautiful emotional tender love heartfelt music",
    "love": "romantic tender emotional beautiful heartfelt gentle music",
    "sad": "melancholic emotional sorrowful gentle piano music",
    "happy": "joyful upbeat cheerful happy positive bright music",

    # Action/Energy
    "action": "intense energetic powerful dramatic epic driving music",
    "sports": "energetic powerful dynamic motivational pump up music",
    "workout": "energetic high tempo powerful motivational beat music",
    "gaming": "energetic electronic intense dynamic exciting game music",
    "game": "energetic electronic dynamic exciting playful music",
    "trailer": "epic cinematic dramatic intense powerful orchestral music",
    "movie": "cinematic orchestral dramatic emotional film score music",
    "film": "cinematic orchestral dramatic emotional soundtrack music",

    # Nature/Relaxation
    "nature": "peaceful ambient relaxing calm natural atmospheric music",
    "relaxation": "calm peaceful soothing gentle ambient relaxing music",
    "meditation": "calm peaceful ambient meditative spiritual gentle music",
    "spa": "relaxing calm soothing peaceful gentle ambient music",
    "sleep": "calm gentle soothing peaceful ambient quiet music",

    # Horror/Scary (kinh dị)
    "horror": "dark tense eerie suspenseful creepy scary atmospheric music",
    "scary": "dark tense eerie suspenseful creepy horror atmospheric music",
    "thriller": "tense suspenseful dark mysterious dramatic music",
    "suspense": "tense suspenseful mysterious dark dramatic music",
    "creepy": "eerie dark atmospheric unsettling mysterious music",
}

# Synonym mappings for query expansion
# Each key maps to a set of related terms
SYNONYM_MAPPINGS: Dict[str, Set[str]] = {
    # Music genres
    "rap": {"hip hop", "rapping vocal", "hip-hop beat"},
    "hip hop": {"rap", "rapping vocal", "hip-hop beat"},
    "hip-hop": {"rap", "hip hop", "rapping vocal"},
    "edm": {"electronic dance music", "electronic beat", "dance music"},
    "electronic dance music": {"edm", "electronic beat", "dance music"},
    "rnb": {"r&b", "rhythm and blues", "soul music"},
    "r&b": {"rnb", "rhythm and blues", "soul music"},
    "lofi": {"lo-fi", "lo fi beats", "chillhop relaxing"},
    "lo-fi": {"lofi", "lo fi beats", "chillhop relaxing"},

    # Weather/nature sounds (for SFX)
    "storm": {"thunder", "thunderstorm", "heavy rain wind"},
    "thunder": {"storm", "thunderstorm", "lightning"},
    "thunderstorm": {"storm", "thunder", "heavy rain"},
    "rain": {"rainfall", "raining", "rainy weather"},
    "wind": {"windy", "gust", "breeze"},

    # Mood/atmosphere
    "scary": {"horror", "creepy eerie", "spooky frightening tense"},
    "horror": {"scary", "creepy eerie", "spooky frightening dark tense"},
    "creepy": {"scary", "horror dark", "eerie spooky"},
    "happy": {"joyful", "cheerful upbeat", "uplifting positive"},
    "sad": {"melancholy", "melancholic emotional", "sorrowful mournful"},
    "epic": {"cinematic dramatic", "grand orchestral", "powerful majestic"},
    "cinematic": {"epic dramatic", "film score", "movie orchestral"},
    "chill": {"relaxing calm", "mellow laid-back", "peaceful ambient"},
    "relaxing": {"chill calm", "peaceful soothing", "gentle ambient"},

    # Instruments
    "guitar": {"acoustic guitar", "electric guitar", "guitar melody"},
    "piano": {"keyboard", "piano melody", "keys instrumental"},
    "drums": {"percussion", "drum beat", "rhythmic drums"},
    "synth": {"synthesizer", "electronic synth", "synth melody"},

    # Tempo/energy
    "fast": {"upbeat", "high tempo energetic", "quick dynamic"},
    "slow": {"slow tempo", "mellow gentle", "laid-back calm"},
    "energetic": {"high energy", "upbeat powerful", "dynamic intense"},
}


class QueryProcessor:
    """
    Process and enhance search queries for better semantic matching.
    """

    def __init__(self, enable_synonyms: bool = True, enable_templates: bool = True):
        """
        Initialize the query processor.

        Args:
            enable_synonyms: Whether to apply synonym expansion
            enable_templates: Whether to generate prompt template variants
        """
        self.enable_synonyms = enable_synonyms
        self.enable_templates = enable_templates
        self._synonym_pattern_cache: Dict[str, re.Pattern] = {}

        logger.info(
            "QueryProcessor initialized: synonyms=%s, templates=%s",
            enable_synonyms,
            enable_templates,
        )

    def process_query(
        self,
        query: str,
        content_type: str,
    ) -> ProcessedQueryResult:
        """
        Process a search query with use-case mapping, synonym expansion and prompt templates.

        Args:
            query: The original search query
            content_type: Either "song" or "sfx"

        Returns:
            ProcessedQueryResult with expanded query and prompt variants
        """
        original = query.strip()
        expanded = original
        synonyms_applied: List[str] = []

        # For music queries, apply use-case to music style mapping first
        if content_type.lower() == "song":
            expanded, use_case_applied = self._apply_use_case_mapping(original)
            if use_case_applied:
                synonyms_applied.append(f"use-case:{use_case_applied}")
                logger.info("Applied use-case mapping: %s -> %s", original, expanded)

        # Apply synonym expansion
        if self.enable_synonyms:
            expanded, syn_applied = self._expand_synonyms(expanded)
            synonyms_applied.extend(syn_applied)

        # Generate prompt variants
        prompt_variants: List[str] = []
        if self.enable_templates:
            templates = (
                SONG_PROMPT_TEMPLATES
                if content_type.lower() == "song"
                else SFX_PROMPT_TEMPLATES
            )
            for template in templates:
                prompt_variants.append(template.format(query=expanded))

        # Always include the expanded query itself as a variant
        if expanded not in prompt_variants:
            prompt_variants.insert(0, expanded)

        return ProcessedQueryResult(
            original_query=original,
            expanded_query=expanded,
            prompt_variants=prompt_variants,
            synonyms_applied=synonyms_applied,
        )

    def _apply_use_case_mapping(self, query: str) -> tuple[str, Optional[str]]:
        """
        Apply use-case to music style mapping.

        Converts contextual queries (e.g., "music for award ceremony")
        to music characteristic queries (e.g., "triumphant orchestral fanfare").

        Returns tuple of (transformed_query, matched_use_case or None)
        """
        query_lower = query.lower()

        # Check for use-case keywords, starting with longer phrases first
        sorted_use_cases = sorted(USE_CASE_MUSIC_MAPPINGS.keys(), key=len, reverse=True)

        for use_case in sorted_use_cases:
            if use_case in query_lower:
                music_style = USE_CASE_MUSIC_MAPPINGS[use_case]
                # Replace the use-case with music characteristics
                # but keep any additional descriptors from the original query
                remaining = query_lower.replace(use_case, "").strip()
                # Remove common filler words
                for filler in ["music for", "song for", "music", "song", "for", "the", "a", "an"]:
                    remaining = remaining.replace(filler, " ")
                remaining = " ".join(remaining.split())  # Clean up whitespace

                if remaining:
                    expanded = f"{music_style} {remaining}"
                else:
                    expanded = music_style

                return expanded, use_case

        return query, None

    def _expand_synonyms(self, query: str) -> tuple[str, List[str]]:
        """
        Expand query with synonyms for known terms.

        Returns tuple of (expanded_query, list_of_synonyms_applied)
        """
        query_lower = query.lower()
        synonyms_applied: List[str] = []
        additions: List[str] = []

        for term, synonyms in SYNONYM_MAPPINGS.items():
            # Check if term appears in query (whole word match)
            pattern = self._get_word_pattern(term)
            if pattern.search(query_lower):
                # Add the most relevant synonym that's not already in the query
                for synonym in synonyms:
                    syn_pattern = self._get_word_pattern(synonym)
                    if not syn_pattern.search(query_lower):
                        additions.append(synonym)
                        synonyms_applied.append(f"{term}→{synonym}")
                        break  # Only add one synonym per term

        if additions:
            # Append synonyms to the query
            expanded = f"{query} {' '.join(additions)}"
            logger.debug(
                "Expanded query: '%s' -> '%s' (synonyms: %s)",
                query,
                expanded,
                synonyms_applied,
            )
            return expanded, synonyms_applied

        return query, []

    def _get_word_pattern(self, word: str) -> re.Pattern:
        """Get or create a compiled regex pattern for whole-word matching."""
        if word not in self._synonym_pattern_cache:
            # Escape special regex characters and create word boundary pattern
            escaped = re.escape(word)
            self._synonym_pattern_cache[word] = re.compile(
                rf"\b{escaped}\b", re.IGNORECASE
            )
        return self._synonym_pattern_cache[word]


def average_embeddings(embeddings: List[np.ndarray]) -> np.ndarray:
    """
    Average multiple embeddings into a single embedding.

    Args:
        embeddings: List of embedding arrays to average

    Returns:
        Single averaged embedding array
    """
    if not embeddings:
        raise ValueError("Cannot average empty list of embeddings")

    if len(embeddings) == 1:
        return embeddings[0]

    stacked = np.stack(embeddings, axis=0)
    averaged = np.mean(stacked, axis=0)

    # Normalize the averaged embedding
    norm = np.linalg.norm(averaged)
    if norm > 0:
        averaged = averaged / norm

    return averaged
