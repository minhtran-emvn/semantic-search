"""
API route handlers for the semantic audio search backend.
"""

import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.models import (
    AudioResult,
    ExamplePrompt,
    ExamplePromptsResponse,
    HealthResponse,
    SearchRequest,
    SearchResponse,
)
from app.core.clap_service import CLAPService
from app.core.content_type_detector import ContentTypeDetector
from app.core.search_service import SearchService
from app.core.translation_service import TranslationService

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)


def get_clap_service(request: Request) -> CLAPService:
    return request.app.state.clap_service


def get_search_service(request: Request) -> SearchService:
    return request.app.state.search_service


def get_translation_service(request: Request) -> TranslationService:
    return request.app.state.translation_service


def get_content_type_detector(request: Request) -> ContentTypeDetector:
    return request.app.state.content_type_detector


def _load_example_prompts() -> list[ExamplePrompt]:
    config_path = Path(__file__).resolve().parents[2] / "config" / "example_prompts.json"
    with config_path.open("r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)
    prompts = data.get("prompts", [])
    return [ExamplePrompt(**prompt) for prompt in prompts]


@router.get("/health", response_model=HealthResponse)
async def health_check(
    clap_service: CLAPService = Depends(get_clap_service),
) -> HealthResponse:
    """Health check endpoint for monitoring service readiness."""
    model_loaded = bool(getattr(clap_service, "model", None))
    return HealthResponse(status="healthy", model_loaded=model_loaded)


@router.get("/example-prompts", response_model=ExamplePromptsResponse)
async def get_example_prompts(
    lang: str | None = None,
    translation_service: TranslationService = Depends(get_translation_service),
) -> ExamplePromptsResponse:
    """Return example prompts, optionally localized."""
    prompts = _load_example_prompts()

    if lang and lang.lower() != "en":
        translated_prompts = []
        try:
            for prompt in prompts:
                result = await translation_service.translate(
                    prompt.text,
                    source_lang="en",
                    target_lang=lang,
                )
                if not result.success:
                    raise RuntimeError(result.error_msg or "Translation failed")
                translated_prompts.append(
                    ExamplePrompt(category=prompt.category, text=result.translated_text)
                )
            prompts = translated_prompts
        except Exception as exc:
            logger.warning("Example prompt translation failed: %s", exc)

    return ExamplePromptsResponse(prompts=prompts)

@router.post("/search", response_model=SearchResponse)
async def search_audio(
    search_request: SearchRequest,
    translation_service: TranslationService = Depends(get_translation_service),
    content_type_detector: ContentTypeDetector = Depends(get_content_type_detector),
    clap_service: CLAPService = Depends(get_clap_service),
    search_service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    """Search endpoint for semantic audio matching."""
    try:
        processed_query = await translation_service.detect_and_translate(
            search_request.query
        )
        english_text = processed_query.english_text
        original_query = processed_query.original_text

        if search_request.content_type:
            content_type = search_request.content_type
        else:
            detection = content_type_detector.detect(english_text)
            content_type = detection.type

        text_embedding = clap_service.get_text_embedding_for_content_type(
            english_text,
            content_type,
        )
        results = search_service.search_by_content_type(
            text_embedding,
            content_type,
            k=search_request.top_k,
        )
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
            content_type=content_type,
        )
        for result in results
    ]

    return SearchResponse(
        results=audio_results,
        query=english_text,
        num_results=len(audio_results),
        content_type=content_type,
        original_query=original_query,
        was_translated=processed_query.was_translated,
        translation_warning=processed_query.translation_warning,
    )
