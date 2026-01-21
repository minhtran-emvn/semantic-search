from unittest.mock import AsyncMock, Mock

import numpy as np
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import router
from app.core.content_type_detector import ContentType
from app.core.search_service import SearchResult
from app.core.translation_service import ProcessedQuery


def _create_app(clap_service, search_service, translation_service, content_type_detector):
    app = FastAPI()
    app.include_router(router)
    app.state.clap_service = clap_service
    app.state.search_service = search_service
    app.state.translation_service = translation_service
    app.state.content_type_detector = content_type_detector
    return app


def test_search_english_query():
    translation_service = Mock()
    translation_service.detect_and_translate = AsyncMock(
        return_value=ProcessedQuery(
        english_text="relaxing piano music",
        original_text="relaxing piano music",
        lang_code="en",
        was_translated=False,
        translation_warning=None,
        )
    )
    content_type_detector = Mock()
    content_type_detector.detect.return_value = ContentType(
        type="song",
        confidence=0.9,
        matched_keywords=["piano"],
    )
    clap_service = Mock()
    clap_service.get_text_embedding_for_content_type.return_value = np.zeros(512)
    search_service = Mock()
    search_service.search_by_content_type.return_value = [
        SearchResult(filename="song.wav", similarity=0.9, audio_url="/audio/song.wav"),
    ]

    app = _create_app(clap_service, search_service, translation_service, content_type_detector)

    with TestClient(app) as client:
        response = client.post("/api/search", json={"query": "relaxing piano music", "top_k": 1})

    assert response.status_code == 200
    payload = response.json()
    assert payload["content_type"] == "song"
    assert payload["was_translated"] is False
    assert payload["original_query"] == "relaxing piano music"
    assert payload["results"][0]["content_type"] == "song"


def test_search_spanish_query_translation():
    translation_service = Mock()
    translation_service.detect_and_translate = AsyncMock(
        return_value=ProcessedQuery(
        english_text="relaxing piano music",
        original_text="musica relajante",
        lang_code="es",
        was_translated=True,
        translation_warning=None,
        )
    )
    content_type_detector = Mock()
    content_type_detector.detect.return_value = ContentType(
        type="song",
        confidence=0.8,
        matched_keywords=["music"],
    )
    clap_service = Mock()
    clap_service.get_text_embedding_for_content_type.return_value = np.zeros(512)
    search_service = Mock()
    search_service.search_by_content_type.return_value = [
        SearchResult(filename="song.wav", similarity=0.9, audio_url="/audio/song.wav"),
    ]

    app = _create_app(clap_service, search_service, translation_service, content_type_detector)

    with TestClient(app) as client:
        response = client.post("/api/search", json={"query": "musica relajante", "top_k": 1})

    assert response.status_code == 200
    payload = response.json()
    assert payload["was_translated"] is True
    assert payload["original_query"] == "musica relajante"
    assert payload["query"] == "relaxing piano music"


def test_search_manual_content_type_override():
    translation_service = Mock()
    translation_service.detect_and_translate = AsyncMock(
        return_value=ProcessedQuery(
        english_text="dramatic explosion",
        original_text="dramatic explosion",
        lang_code="en",
        was_translated=False,
        translation_warning=None,
        )
    )
    content_type_detector = Mock()
    content_type_detector.detect.return_value = ContentType(
        type="song",
        confidence=0.5,
        matched_keywords=[],
    )
    clap_service = Mock()
    clap_service.get_text_embedding_for_content_type.return_value = np.zeros(512)
    search_service = Mock()
    search_service.search_by_content_type.return_value = [
        SearchResult(filename="boom.wav", similarity=0.8, audio_url="/audio/boom.wav"),
    ]

    app = _create_app(clap_service, search_service, translation_service, content_type_detector)

    with TestClient(app) as client:
        response = client.post(
            "/api/search",
            json={"query": "dramatic explosion", "top_k": 1, "content_type": "sfx"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["content_type"] == "sfx"
    search_service.search_by_content_type.assert_called_with(
        clap_service.get_text_embedding_for_content_type.return_value,
        "sfx",
        k=1,
    )


def test_search_translation_warning_on_failure():
    translation_service = Mock()
    translation_service.detect_and_translate = AsyncMock(
        return_value=ProcessedQuery(
        english_text="音楽",
        original_text="音楽",
        lang_code="ja",
        was_translated=False,
        translation_warning="Translation unavailable. Searching with original text may yield less accurate results.",
        )
    )
    content_type_detector = Mock()
    content_type_detector.detect.return_value = ContentType(
        type="song",
        confidence=0.5,
        matched_keywords=[],
    )
    clap_service = Mock()
    clap_service.get_text_embedding_for_content_type.return_value = np.zeros(512)
    search_service = Mock()
    search_service.search_by_content_type.return_value = []

    app = _create_app(clap_service, search_service, translation_service, content_type_detector)

    with TestClient(app) as client:
        response = client.post("/api/search", json={"query": "音楽", "top_k": 1})

    assert response.status_code == 200
    payload = response.json()
    assert payload["translation_warning"] is not None
