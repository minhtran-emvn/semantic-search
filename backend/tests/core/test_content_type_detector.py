import json

from app.core.content_type_detector import ContentTypeDetector


def _write_keywords(tmp_path):
    config = {
        "music_keywords": ["music", "piano"],
        "sfx_keywords": ["explosion", "sound effect"],
    }
    config_path = tmp_path / "detection_keywords.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return config_path


def test_detect_music_keywords(tmp_path):
    config_path = _write_keywords(tmp_path)
    detector = ContentTypeDetector(keywords_config_path=str(config_path))

    result = detector.detect("relaxing piano music")

    assert result.type == "song"
    assert result.confidence > 0.5


def test_detect_sfx_keywords(tmp_path):
    config_path = _write_keywords(tmp_path)
    detector = ContentTypeDetector(keywords_config_path=str(config_path))

    result = detector.detect("explosion sound effect")

    assert result.type == "sfx"
    assert result.confidence > 0.5


def test_detect_ambiguous_defaults_to_song(tmp_path):
    config_path = _write_keywords(tmp_path)
    detector = ContentTypeDetector(keywords_config_path=str(config_path))

    result = detector.detect("calm atmosphere")

    assert result.type == "song"
    assert result.confidence == 0.0


def test_detect_mixed_keywords_count_based(tmp_path):
    config_path = _write_keywords(tmp_path)
    detector = ContentTypeDetector(keywords_config_path=str(config_path))

    result = detector.detect("piano explosion sound effect")

    assert result.type == "sfx"
    assert result.confidence > 0.6


def test_detect_confidence_calculation(tmp_path):
    config_path = _write_keywords(tmp_path)
    detector = ContentTypeDetector(keywords_config_path=str(config_path))

    result = detector.detect("piano explosion")

    assert result.type == "song"
    assert result.confidence == 0.5
