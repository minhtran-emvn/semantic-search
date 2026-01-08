"""
Pydantic models for API request/response validation.

This module defines type-safe API contracts with automatic validation
for the Semantic Audio Search Engine.
"""

from pydantic import BaseModel, Field
from typing import List


class SearchRequest(BaseModel):
    """Request model for semantic audio search.

    Attributes:
        query: Natural language search query (1-500 characters, ~77 tokens max)
        top_k: Number of top results to return (1-100, default 5)
    """
    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Natural language search query"
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Number of top results to return"
    )


class AudioResult(BaseModel):
    """Individual audio search result.

    Attributes:
        filename: Name/title of the audio file
        similarity: Similarity score between 0.0 and 1.0
        audio_url: URL path to access the audio file
    """
    filename: str = Field(..., description="Audio file name/title")
    similarity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity score (0.0-1.0)"
    )
    audio_url: str = Field(..., description="URL to access the audio file")


class SearchResponse(BaseModel):
    """Response model for semantic audio search.

    Attributes:
        results: List of audio search results ordered by similarity
        query: Original search query that was processed
        num_results: Total number of results returned
    """
    results: List[AudioResult] = Field(
        ...,
        description="List of audio search results"
    )
    query: str = Field(..., description="Original search query")
    num_results: int = Field(..., description="Total number of results")


class HealthResponse(BaseModel):
    """Response model for health check endpoint.

    Attributes:
        status: Overall health status of the API
        model_loaded: Whether the CLAP model is loaded and ready
    """
    status: str = Field(..., description="Overall health status")
    model_loaded: bool = Field(
        ...,
        description="Whether CLAP model is loaded and ready"
    )
