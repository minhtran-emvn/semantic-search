import json
from pathlib import Path

import faiss
import numpy as np

from app.core import search_service
from app.core.search_service import SearchService


def _make_embeddings(indices):
    embeddings = np.zeros((len(indices), 512), dtype="float32")
    for row, index in enumerate(indices):
        embeddings[row, index] = 1.0
    return embeddings


def test_build_music_index_creates_index(monkeypatch, tmp_path):
    music_dir = tmp_path / "music"
    music_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(search_service.settings, "MUSIC_EMBEDDINGS_DIR", music_dir)

    service = SearchService(tmp_path / "sfx")
    embeddings = _make_embeddings([0, 1, 2])
    metadata = {"filenames": ["a.wav", "b.wav", "c.wav"], "file_paths": ["a", "b", "c"]}

    service.build_music_index(embeddings, metadata)

    assert service.music_index is not None
    assert service.music_index.ntotal == 3


def test_load_music_index(monkeypatch, tmp_path):
    music_dir = tmp_path / "music"
    music_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(search_service.settings, "MUSIC_EMBEDDINGS_DIR", music_dir)

    embeddings = _make_embeddings([0, 1])
    index = faiss.IndexFlatIP(512)
    index.add(embeddings)
    faiss.write_index(index, str(music_dir / "index.faiss"))

    metadata = {"filenames": ["one.wav", "two.wav"], "file_paths": ["one", "two"]}
    (music_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

    service = SearchService(tmp_path / "sfx")
    loaded = service.load_music_index()

    assert loaded is True
    assert service.music_index is not None
    assert service.music_metadata["filenames"] == ["one.wav", "two.wav"]


def test_search_by_content_type_selects_index(monkeypatch, tmp_path):
    music_dir = tmp_path / "music"
    music_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(search_service.settings, "MUSIC_EMBEDDINGS_DIR", music_dir)

    service = SearchService(tmp_path / "sfx")

    sfx_embeddings = _make_embeddings([0, 2])
    sfx_metadata = {"filenames": ["sfx_one.wav", "sfx_two.wav"], "file_paths": ["s1", "s2"]}
    service.build_index(sfx_embeddings)
    service.metadata = sfx_metadata

    music_embeddings = _make_embeddings([1, 3])
    music_metadata = {
        "filenames": ["song_one.wav", "song_two.wav"],
        "file_paths": ["m1", "m2"],
    }
    service.build_music_index(music_embeddings, music_metadata)

    song_results = service.search_by_content_type(music_embeddings[0], "song", k=1)
    sfx_results = service.search_by_content_type(sfx_embeddings[0], "sfx", k=1)

    assert song_results[0].filename == "song_one.wav"
    assert sfx_results[0].filename == "sfx_one.wav"
