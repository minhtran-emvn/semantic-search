from unittest.mock import Mock

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.search_service import SearchResult


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_clap_service():
    service = Mock()
    service.get_text_embedding.return_value = np.random.rand(512).astype("float32")
    service.model = object()
    return service


@pytest.fixture
def mock_search_service():
    service = Mock()
    service.search.return_value = [
        SearchResult(
            filename="rainstorm.wav",
            similarity=0.92,
            audio_url="/audio/rainstorm.wav",
        ),
        SearchResult(
            filename="wind_chimes.wav",
            similarity=0.87,
            audio_url="/audio/wind_chimes.wav",
        ),
    ]
    return service
