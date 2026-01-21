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
SONG_PROMPT_TEMPLATES = [
    "This is a {query} song",
    "This music features {query}",
    "Music with {query}",
    "{query} music track",
]

SFX_PROMPT_TEMPLATES = [
    "This is a sound of {query}",
    "Sound effect of {query}",
    "The sound of {query}",
    "{query} sound",
]

# Synonym mappings for query expansion
# Each key maps to a set of related terms
SYNONYM_MAPPINGS: Dict[str, Set[str]] = {
    # Music genres
    "rap": {"hip hop", "rapping", "rapper", "hip-hop"},
    "hip hop": {"rap", "rapping", "rapper", "hip-hop"},
    "hip-hop": {"rap", "hip hop", "rapping"},
    "edm": {"electronic dance music", "electronic", "dance music"},
    "electronic dance music": {"edm", "electronic", "dance music"},
    "rnb": {"r&b", "rhythm and blues", "r and b"},
    "r&b": {"rnb", "rhythm and blues", "r and b"},
    "lofi": {"lo-fi", "lo fi", "chillhop"},
    "lo-fi": {"lofi", "lo fi", "chillhop"},

    # Weather/nature sounds
    "storm": {"thunder", "thunderstorm", "lightning", "heavy rain", "wind"},
    "thunder": {"storm", "thunderstorm", "lightning"},
    "thunderstorm": {"storm", "thunder", "lightning", "heavy rain"},
    "rain": {"rainfall", "raining", "rainy", "drizzle"},
    "wind": {"windy", "gust", "breeze", "stormy"},

    # Mood/atmosphere
    "scary": {"horror", "creepy", "eerie", "spooky", "frightening"},
    "horror": {"scary", "creepy", "eerie", "spooky", "frightening", "terrifying"},
    "creepy": {"scary", "horror", "eerie", "spooky"},
    "happy": {"joyful", "cheerful", "upbeat", "uplifting"},
    "sad": {"melancholy", "melancholic", "sorrowful", "mournful"},
    "epic": {"cinematic", "dramatic", "grand", "orchestral"},
    "cinematic": {"epic", "dramatic", "film score", "movie"},
    "chill": {"relaxing", "calm", "mellow", "laid-back"},
    "relaxing": {"chill", "calm", "peaceful", "soothing"},

    # Instruments
    "guitar": {"acoustic guitar", "electric guitar", "guitar riff"},
    "piano": {"keyboard", "piano melody", "keys"},
    "drums": {"percussion", "drum beat", "drumming"},
    "synth": {"synthesizer", "electronic", "synths"},

    # Tempo/energy
    "fast": {"upbeat", "high tempo", "energetic", "quick"},
    "slow": {"slow tempo", "mellow", "laid-back"},
    "energetic": {"high energy", "upbeat", "powerful", "dynamic"},
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
        Process a search query with synonym expansion and prompt templates.

        Args:
            query: The original search query
            content_type: Either "song" or "sfx"

        Returns:
            ProcessedQueryResult with expanded query and prompt variants
        """
        original = query.strip()
        expanded = original
        synonyms_applied: List[str] = []

        # Apply synonym expansion
        if self.enable_synonyms:
            expanded, synonyms_applied = self._expand_synonyms(original)

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
