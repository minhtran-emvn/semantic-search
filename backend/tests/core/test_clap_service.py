import numpy as np

from app.core import clap_service


class _DummyInnerModel:
    def __init__(self):
        self.moves = []

    def to(self, device):
        self.moves.append(device)


class _DummyCLAPModule:
    load_attempts = 0

    def __init__(self, device=None, enable_fusion=None, amodel=None, tmodel=None):
        self.device = device
        self.model = _DummyInnerModel()

    def load_ckpt(self, ckpt=None):
        _DummyCLAPModule.load_attempts += 1
        if _DummyCLAPModule.load_attempts < 2:
            raise RuntimeError("load failed")


class _DummyEmbeddingModel:
    def __init__(self, value):
        self.value = value
        self.model = _DummyInnerModel()

    def get_text_embedding(self, texts, use_tensor=False):
        return np.array([self.value], dtype="float32")


def test_load_music_model_retries(monkeypatch):
    monkeypatch.setattr(clap_service, "CLAP_Module", _DummyCLAPModule)
    _DummyCLAPModule.load_attempts = 0

    service = clap_service.CLAPService(device="cpu")
    service.load_music_model()

    assert service.music_model is not None
    assert _DummyCLAPModule.load_attempts == 2


def test_get_text_embedding_for_song_and_sfx():
    service = clap_service.CLAPService(device="cpu")
    service.model = _DummyEmbeddingModel([0.1, 0.2, 0.3])
    service.music_model = _DummyEmbeddingModel([0.9, 0.8, 0.7])

    song_embedding = service.get_text_embedding_for_content_type("query", "song")
    sfx_embedding = service.get_text_embedding_for_content_type("query", "sfx")

    assert song_embedding.tolist() == [0.9, 0.8, 0.7]
    assert sfx_embedding.tolist() == [0.1, 0.2, 0.3]


def test_swap_models_for_low_memory():
    service = clap_service.CLAPService(device="cuda")
    service.device_memory = 2.0
    service.model = _DummyEmbeddingModel([0.1, 0.2])
    service.music_model = _DummyEmbeddingModel([0.9, 0.8])

    service._swap_models_if_needed("song")

    assert service.music_model.model.moves[-1] == "cuda"
    assert service.model.model.moves[-1] == "cpu"


def test_fallback_to_sfx_model_when_music_missing():
    service = clap_service.CLAPService(device="cpu")
    service.model = _DummyEmbeddingModel([0.1, 0.2, 0.3])
    service.music_model = None

    embedding = service.get_text_embedding_for_content_type("query", "song")

    assert embedding.tolist() == [0.1, 0.2, 0.3]
