"""
Pydantic models for API request/response validation.

This module defines type-safe API contracts with automatic validation
for the Semantic Audio Search Engine.
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional


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
    content_type: Optional[Literal["song", "sfx"]] = Field(
        default=None,
        description="Optional manual content type override"
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
    content_type: str = Field(
        ...,
        description="Content type for the audio result (song or sfx)"
    )


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
    content_type: str = Field(..., description="Resolved content type for the search")
    original_query: str = Field(..., description="Original user input (pre-translation)")
    was_translated: bool = Field(..., description="Whether translation was applied")
    translation_warning: Optional[str] = Field(
        default=None,
        description="Warning message when translation degrades"
    )


class ExamplePrompt(BaseModel):
    """Example prompt model for UI suggestions."""

    category: str = Field(..., description="Prompt category label")
    text: str = Field(..., description="Example prompt text")


class ExamplePromptsResponse(BaseModel):
    """Response model for example prompts."""

    prompts: List[ExamplePrompt] = Field(
        ...,
        description="List of example prompts grouped by category"
    )


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
