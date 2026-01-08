"""
API route handlers for the semantic audio search backend.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.models import AudioResult, HealthResponse, SearchRequest, SearchResponse
from app.core.clap_service import CLAPService
from app.core.search_service import SearchService

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)


def get_clap_service(request: Request) -> CLAPService:
    return request.app.state.clap_service


def get_search_service(request: Request) -> SearchService:
    return request.app.state.search_service


@router.get("/health", response_model=HealthResponse)
async def health_check(
    clap_service: CLAPService = Depends(get_clap_service),
) -> HealthResponse:
    """Health check endpoint for monitoring service readiness."""
    model_loaded = bool(getattr(clap_service, "model", None))
    return HealthResponse(status="healthy", model_loaded=model_loaded)


@router.post("/search", response_model=SearchResponse)
async def search_audio(
    search_request: SearchRequest,
    clap_service: CLAPService = Depends(get_clap_service),
    search_service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    """Search endpoint for semantic audio matching."""
    try:
        text_embedding = clap_service.get_text_embedding(search_request.query)
        results = search_service.search(text_embedding, k=search_request.top_k)
    except Exception as exc:
        logger.exception("Search request failed")
        raise HTTPException(
            status_code=500,
            detail="Search service failure",
        ) from exc

    audio_results = [
        AudioResult(
            filename=result.filename,
            similarity=result.similarity,
            audio_url=result.audio_url,
        )
        for result in results
    ]

    return SearchResponse(
        results=audio_results,
        query=search_request.query,
        num_results=len(audio_results),
    )
