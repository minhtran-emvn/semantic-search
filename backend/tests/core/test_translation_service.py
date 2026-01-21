import asyncio

from app.core.translation_service import (
    LanguageDetectionResult,
    TranslationResult,
    TranslationService,
)


def test_detect_language_english():
    service = TranslationService(provider="google", api_key="test-key")

    async def fake_detect_google(text, timeout_seconds):
        return {"lang_code": "en", "confidence": 0.95}

    service._detect_google = fake_detect_google
    result = asyncio.run(service.detect_language("hello world"))

    assert result.lang_code == "en"
    assert result.is_english is True


def test_detect_language_spanish():
    service = TranslationService(provider="google", api_key="test-key")

    async def fake_detect_google(text, timeout_seconds):
        return {"lang_code": "es", "confidence": 0.92}

    service._detect_google = fake_detect_google
    result = asyncio.run(service.detect_language("hola mundo"))

    assert result.lang_code == "es"
    assert result.is_english is False


def test_detect_language_japanese():
    service = TranslationService(provider="google", api_key="test-key")

    async def fake_detect_google(text, timeout_seconds):
        return {"lang_code": "ja", "confidence": 0.9}

    service._detect_google = fake_detect_google
    result = asyncio.run(service.detect_language("こんにちは"))

    assert result.lang_code == "ja"
    assert result.is_english is False


def test_detect_language_chinese():
    service = TranslationService(provider="google", api_key="test-key")

    async def fake_detect_google(text, timeout_seconds):
        return {"lang_code": "zh", "confidence": 0.91}

    service._detect_google = fake_detect_google
    result = asyncio.run(service.detect_language("你好"))

    assert result.lang_code == "zh"
    assert result.is_english is False


def test_translate_success():
    service = TranslationService(provider="google", api_key="test-key")

    async def fake_translate_google(text, source_lang, target_lang, timeout_seconds):
        return "hello world"

    service._translate_google = fake_translate_google
    result = asyncio.run(service.translate("hola mundo", "es"))

    assert result.success is True
    assert result.translated_text == "hello world"


def test_translate_rate_limit_failure():
    service = TranslationService(provider="google", api_key="test-key")

    async def fake_translate_google(text, source_lang, target_lang, timeout_seconds):
        raise RuntimeError("HTTP Error 429: Too Many Requests")

    service._translate_google = fake_translate_google
    result = asyncio.run(service.translate("hola mundo", "es"))

    assert result.success is False
    assert result.error_msg == "Rate limit exceeded"


def test_translate_generic_failure():
    service = TranslationService(provider="google", api_key="test-key")

    async def fake_translate_google(text, source_lang, target_lang, timeout_seconds):
        raise RuntimeError("HTTP Error 503: Service Unavailable")

    service._translate_google = fake_translate_google
    result = asyncio.run(service.translate("hola mundo", "es"))

    assert result.success is False
    assert "HTTP Error 503" in result.error_msg


def test_detect_and_translate_skips_english():
    service = TranslationService(provider="google", api_key="test-key")

    async def fake_detect_language(text):
        return LanguageDetectionResult(lang_code="en", confidence=0.9, is_english=True)

    async def fake_translate(text, source_lang):
        raise AssertionError("translate should not be called for English text")

    service.detect_language = fake_detect_language
    service.translate = fake_translate
    result = asyncio.run(service.detect_and_translate("hello world"))

    assert result.was_translated is False
    assert result.english_text == "hello world"
    assert result.lang_code == "en"


def test_detect_and_translate_non_english():
    service = TranslationService(provider="google", api_key="test-key")

    async def fake_detect_language(text):
        return LanguageDetectionResult(lang_code="es", confidence=0.9, is_english=False)

    async def fake_translate(text, source_lang):
        return TranslationResult(translated_text="hello world", success=True)

    service.detect_language = fake_detect_language
    service.translate = fake_translate
    result = asyncio.run(service.detect_and_translate("hola mundo"))

    assert result.was_translated is True
    assert result.english_text == "hello world"
    assert result.lang_code == "es"


def test_detect_and_translate_empty_text():
    service = TranslationService(provider="google", api_key="test-key")
    result = asyncio.run(service.detect_and_translate("   "))

    assert result.was_translated is False
    assert result.english_text == "   "
    assert result.original_text == "   "


def test_detect_and_translate_emoji_only():
    service = TranslationService(provider="google", api_key="test-key")
    result = asyncio.run(service.detect_and_translate("🙂🙂"))

    assert result.was_translated is False
    assert result.english_text == "🙂🙂"
    assert result.lang_code == "und"


def test_detect_and_translate_low_confidence():
    service = TranslationService(provider="google", api_key="test-key")

    async def fake_detect_language(text):
        return LanguageDetectionResult(lang_code="es", confidence=0.4, is_english=False)

    async def fake_translate(text, source_lang):
        return TranslationResult(translated_text="hello", success=True)

    service.detect_language = fake_detect_language
    service.translate = fake_translate
    result = asyncio.run(service.detect_and_translate("hola"))

    assert result.was_translated is True
    assert result.english_text == "hello"


def test_detect_and_translate_timeout_warning():
    service = TranslationService(provider="google", api_key="test-key")

    async def fake_detect_language(text):
        return LanguageDetectionResult(lang_code="es", confidence=0.9, is_english=False)

    async def fake_translate(text, source_lang):
        return TranslationResult(translated_text=text, success=False, error_msg="Timeout")

    service.detect_language = fake_detect_language
    service.translate = fake_translate
    result = asyncio.run(service.detect_and_translate("hola"))

    assert result.was_translated is False
    assert result.translation_warning is not None
    assert "Translation unavailable" in result.translation_warning


def test_detect_and_translate_rate_limit_warning():
    service = TranslationService(provider="google", api_key="test-key")

    async def fake_detect_language(text):
        return LanguageDetectionResult(lang_code="es", confidence=0.9, is_english=False)

    async def fake_translate(text, source_lang):
        return TranslationResult(
            translated_text=text,
            success=False,
            error_msg="Rate limit exceeded",
        )

    service.detect_language = fake_detect_language
    service.translate = fake_translate
    result = asyncio.run(service.detect_and_translate("hola"))

    assert result.was_translated is False
    assert result.translation_warning is not None
    assert "rate limit" in result.translation_warning.lower()
