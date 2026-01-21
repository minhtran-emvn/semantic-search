from unittest.mock import AsyncMock, Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import router
from app.core.translation_service import TranslationResult


def _create_app(translation_service):
    app = FastAPI()
    app.include_router(router)
    app.state.translation_service = translation_service
    return app


def test_example_prompts_default_language():
    translation_service = Mock()
    translation_service.translate = AsyncMock()
    app = _create_app(translation_service)

    with TestClient(app) as client:
        response = client.get("/api/example-prompts")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["prompts"]) == 4
    categories = {prompt["category"] for prompt in payload["prompts"]}
    assert "Mood/Emotion" in categories


def test_example_prompts_translation():
    translation_service = Mock()

    async def _translate(text, source_lang, target_lang="en"):
        return TranslationResult(translated_text=f"ES {text}", success=True)

    translation_service.translate = AsyncMock(side_effect=_translate)
    app = _create_app(translation_service)

    with TestClient(app) as client:
        response = client.get("/api/example-prompts?lang=es")

    assert response.status_code == 200
    payload = response.json()
    assert payload["prompts"][0]["text"].startswith("ES ")
    assert translation_service.translate.call_count == 4


def test_example_prompts_translation_failure_fallback():
    translation_service = Mock()
    translation_service.translate = AsyncMock(
        return_value=TranslationResult(
        translated_text="",
        success=False,
        error_msg="Translation failed",
        )
    )
    app = _create_app(translation_service)

    with TestClient(app) as client:
        response = client.get("/api/example-prompts?lang=es")

    assert response.status_code == 200
    payload = response.json()
    assert payload["prompts"][0]["text"].startswith("ES ") is False
