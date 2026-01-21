"""
Translation service data models and configuration.

_Requirements: 7.1, 7.2, 7.3, 7.10_
"""

import asyncio
import json
import logging
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, Optional
from urllib import error as urlerror
from urllib import request as urlrequest


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LanguageDetectionResult:
    lang_code: str
    confidence: float
    is_english: bool


@dataclass(frozen=True)
class TranslationResult:
    translated_text: str
    success: bool
    error_msg: Optional[str] = None


@dataclass(frozen=True)
class ProcessedQuery:
    english_text: str
    original_text: str
    lang_code: str
    was_translated: bool
    translation_warning: Optional[str] = None


class TranslationService:
    """
    Translation service with provider-specific configuration.
    """

    _SUPPORTED_PROVIDERS = {"google", "googletrans", "deepl"}
    # Vietnamese glossary - longer phrases MUST come before shorter ones
    _VI_GLOSSARY = (
        # Weather/Nature
        ("sấm sét", "thunder and lightning"),
        ("sấm", "thunder"),
        ("sét", "lightning"),
        ("bão", "storm"),
        ("mưa rào", "heavy rain"),
        ("mưa", "rain"),
        ("gió", "wind"),
        ("sóng biển", "ocean waves"),
        ("sóng", "waves"),
        ("nước chảy", "flowing water"),
        ("nước", "water"),
        ("lửa", "fire"),
        # Vehicle/Transport sounds
        ("còi xe hơi", "car horn"),
        ("còi xe", "car horn"),
        ("còi tàu", "train horn"),
        ("còi", "horn"),
        ("xe hơi", "car"),
        ("xe máy", "motorcycle"),
        ("xe", "vehicle"),
        ("động cơ", "engine"),
        ("máy bay", "airplane"),
        ("tàu hỏa", "train"),
        ("tàu", "ship"),
        # Animals
        ("chó sủa", "dog barking"),
        ("chó", "dog"),
        ("mèo kêu", "cat meowing"),
        ("mèo", "cat"),
        ("chim hót", "bird singing"),
        ("chim", "bird"),
        ("gà gáy", "rooster crowing"),
        ("gà", "chicken"),
        # Human sounds
        ("tiếng cười", "laughter"),
        ("tiếng khóc", "crying"),
        ("vỗ tay", "applause"),
        ("la hét", "screaming"),
        ("nói chuyện", "talking"),
        ("hát", "singing"),
        # Objects/Actions
        ("cửa đóng", "door closing"),
        ("cửa", "door"),
        ("chuông", "bell"),
        ("đồng hồ", "clock"),
        ("điện thoại", "phone"),
        ("bước chân", "footsteps"),
        ("nổ", "explosion"),
        ("súng", "gunshot"),
        ("kính vỡ", "glass breaking"),
        # Music related
        ("nhạc tết", "festive new year music"),
        ("nhạc xuân", "spring festival music"),
        ("nhạc năm mới", "new year music"),
        ("nhạc kinh dị", "horror music"),
        ("nhạc buồn", "sad music"),
        ("nhạc vui", "happy music"),
        ("nhạc sôi động", "energetic music"),
        ("nhạc nhẹ nhàng", "gentle relaxing music"),
        ("nhạc nền", "background music"),
        ("nhạc phim", "film music soundtrack"),
        ("nhạc quảng cáo", "commercial advertisement music"),
        ("nhạc trao giải", "award ceremony triumphant music"),
        ("nhạc lễ trao giải", "award ceremony triumphant fanfare music"),
        ("nhạc", "music"),
        ("bài hát", "song"),
        ("ca khúc", "song"),
        ("rap", "rap"),
        ("hip hop", "hip hop"),
        ("hip-hop", "hip hop"),
    )
    _VI_SOUND_MARKERS = ("tiếng", "âm thanh")
    _VI_KEYWORDS = (
        # Nature
        "rain", "storm", "thunder", "lightning", "wind", "water", "waves", "fire",
        # Vehicles
        "horn", "car", "vehicle", "engine", "motorcycle", "airplane", "train",
        # Animals
        "dog", "cat", "bird", "chicken", "barking", "meowing",
        # Human
        "laughter", "crying", "applause", "screaming", "footsteps",
        # Objects
        "door", "bell", "phone", "explosion", "gunshot", "glass",
        # Music
        "music", "song", "rap", "hip hop", "soundtrack",
    )

    _DEFAULT_ENDPOINTS: Dict[str, Dict[str, Optional[str]]] = {
        "google": {
            "translate_url": "https://translation.googleapis.com/language/translate/v2",
            "detect_url": "https://translation.googleapis.com/language/translate/v2/detect",
        },
        "googletrans": {
            "translate_url": None,
            "detect_url": None,
        },
        "deepl": {
            "translate_url": "https://api-free.deepl.com/v2/translate",
            "detect_url": None,
        },
    }

    def __init__(
        self,
        provider: str,
        api_key: str,
        api_url: Optional[str] = None,
        allowed_langs: Optional[list[str]] = None,
    ):
        """
        Initialize translation service with configurable provider.

        Args:
            provider: Translation provider ("google", "googletrans", "deepl")
            api_key: API key for the provider
            api_url: Optional base URL override for provider endpoints
        """
        if not provider:
            raise ValueError("Translation provider is required.")

        normalized_provider = provider.strip().lower()
        if normalized_provider not in self._SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported translation provider: {provider}. "
                f"Supported: {sorted(self._SUPPORTED_PROVIDERS)}"
            )

        if normalized_provider in {"google", "deepl"} and not api_key:
            raise ValueError(f"API key is required for provider: {normalized_provider}")

        self.provider = normalized_provider
        self.api_key = api_key or ""
        self.api_url = api_url
        self.endpoints = self._build_endpoints(normalized_provider, api_url)
        self._googletrans_client = None
        if allowed_langs:
            self.allowed_langs = {
                lang.strip().lower()
                for lang in allowed_langs
                if isinstance(lang, str) and lang.strip()
            }
        else:
            self.allowed_langs = None
        self._translation_cache: OrderedDict[
            tuple[str, str, str], tuple[str, float]
        ] = OrderedDict()
        self._language_cache: OrderedDict[str, tuple[LanguageDetectionResult, float]] = (
            OrderedDict()
        )
        self._cache_ttl_seconds = 3600
        self._cache_max_size = 1000

        logger.info(
            "Translation service initialized with provider=%s, translate_url=%s",
            self.provider,
            self.endpoints.get("translate_url"),
        )

    def _build_endpoints(
        self, provider: str, api_url: Optional[str]
    ) -> Dict[str, Optional[str]]:
        if provider == "googletrans":
            return dict(self._DEFAULT_ENDPOINTS[provider])

        if api_url:
            base_url = api_url.rstrip("/")
            if provider == "google":
                return {
                    "translate_url": base_url,
                    "detect_url": f"{base_url}/detect",
                }
            return {
                "translate_url": base_url,
                "detect_url": None,
            }

        return dict(self._DEFAULT_ENDPOINTS[provider])

    async def detect_language(self, text: str) -> LanguageDetectionResult:
        """
        Detect language of input text.

        _Requirements: 7.1, 7.6, 7.12_
        """
        timeout_seconds = 2.0
        trimmed = text.strip()
        if not trimmed:
            return LanguageDetectionResult(lang_code="en", confidence=0.0, is_english=True)

        cached_detection = self._get_cached_detection(trimmed)
        if cached_detection is not None:
            return cached_detection

        try:
            if self.provider == "google":
                detection = await self._detect_google(trimmed, timeout_seconds)
            elif self.provider == "googletrans":
                detection = await self._detect_googletrans(trimmed)
            else:
                detection = await self._detect_deepl(trimmed, timeout_seconds)

            lang_code = (detection.get("lang_code") or "en").lower()
            confidence = float(detection.get("confidence") or 0.0)
            confidence = max(0.0, min(confidence, 1.0))
            is_english = lang_code == "en"

            if confidence and confidence < 0.7:
                logger.warning(
                    "Low-confidence language detection: lang=%s confidence=%.2f",
                    lang_code,
                    confidence,
                )

            result = LanguageDetectionResult(
                lang_code=lang_code, confidence=confidence, is_english=is_english
            )
            self._set_cached_detection(trimmed, result)
            return result
        except Exception as exc:
            logger.warning("Language detection failed, defaulting to English: %s", exc)
            return LanguageDetectionResult(lang_code="en", confidence=0.0, is_english=True)

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str = "en",
    ) -> TranslationResult:
        """
        Translate text from source_lang to English.

        _Requirements: 7.3, 7.7, 7.14, 7.15_
        """
        timeout_seconds = 2.0
        trimmed = text.strip()
        if not trimmed:
            return TranslationResult(translated_text=text, success=True)

        normalized_lang = (source_lang or "").strip().lower()
        normalized_target = (target_lang or "en").strip().lower()
        if not normalized_lang:
            normalized_lang = "auto"
        if normalized_lang not in {"auto"} and normalized_lang == normalized_target:
            return TranslationResult(translated_text=text, success=True)

        cache_key = (normalized_lang, normalized_target, trimmed)
        cached_value = self._get_cached_translation(cache_key)
        if cached_value is not None:
            return TranslationResult(translated_text=cached_value, success=True)

        try:
            if self.provider == "google":
                translated_text = await self._translate_google(
                    trimmed, normalized_lang, normalized_target, timeout_seconds
                )
            elif self.provider == "googletrans":
                translated_text = await self._translate_googletrans(
                    trimmed, normalized_lang, normalized_target
                )
            else:
                translated_text = await self._translate_deepl(
                    trimmed, normalized_lang, normalized_target, timeout_seconds
                )

            self._set_cached_translation(cache_key, translated_text)
            return TranslationResult(translated_text=translated_text, success=True)
        except Exception as exc:
            error_msg = str(exc)
            if "HTTP Error 429" in error_msg or "rate limit" in error_msg.lower():
                error_msg = "Rate limit exceeded"
            logger.warning("Translation failed for lang=%s: %s", normalized_lang, error_msg)
            return TranslationResult(translated_text=text, success=False, error_msg=error_msg)

    async def detect_and_translate(self, text: str) -> ProcessedQuery:
        """
        Detect language and translate to English when needed.

        _Requirements: 7.1, 7.2, 7.3, 7.4, 7.7, 7.8, 7.11, 7.12, 7.14, 7.15, 7.16_
        """
        original_text = text
        trimmed = text.strip()

        if not trimmed:
            return ProcessedQuery(
                english_text=original_text,
                original_text=original_text,
                lang_code="en",
                was_translated=False,
            )

        if self._is_non_textual(trimmed):
            return ProcessedQuery(
                english_text=original_text,
                original_text=original_text,
                lang_code="und",
                was_translated=False,
            )

        # Check if text contains non-ASCII characters (likely non-English)
        has_non_ascii = self._contains_non_ascii_letters(trimmed)
        force_translation = has_non_ascii

        detection_text = self._extract_dominant_text(trimmed)
        detection = await self.detect_language(detection_text)
        lang_code = detection.lang_code or "en"

        # Override language detection if text has non-ASCII letters but was detected as English
        # This handles cases like short Vietnamese queries ("bão") being misdetected
        if force_translation and detection.is_english:
            # Try to infer language from character ranges
            inferred_lang = self._infer_language_from_characters(trimmed)
            if inferred_lang:
                lang_code = inferred_lang
                logger.info(
                    "Overriding language detection: detected=%s, inferred=%s for text: %s",
                    detection.lang_code,
                    inferred_lang,
                    trimmed[:50],
                )

        # Skip translation only if truly English (no non-ASCII letters)
        if detection.is_english and not force_translation:
            return ProcessedQuery(
                english_text=original_text,
                original_text=original_text,
                lang_code=lang_code,
                was_translated=False,
            )

        if (
            force_translation
            and self.allowed_langs == {"vi"}
            and lang_code not in self.allowed_langs
        ):
            lang_code = "vi"

        if self.allowed_langs is not None and lang_code not in self.allowed_langs:
            return ProcessedQuery(
                english_text=original_text,
                original_text=original_text,
                lang_code=lang_code,
                was_translated=False,
            )

        source_lang = "auto" if force_translation and lang_code == "en" else lang_code
        translation = await self.translate(trimmed, source_lang)
        if not translation.success:
            if force_translation and lang_code == "vi":
                glossary_hint = self._apply_vietnamese_glossary(trimmed)
                if glossary_hint:
                    warning = "Translation unavailable. Using Vietnamese keyword fallback."
                    return ProcessedQuery(
                        english_text=glossary_hint,
                        original_text=original_text,
                        lang_code=lang_code,
                        was_translated=True,
                        translation_warning=warning,
                    )

            warning = self._build_translation_warning(translation.error_msg)
            return ProcessedQuery(
                english_text=original_text,
                original_text=original_text,
                lang_code=lang_code,
                was_translated=False,
                translation_warning=warning,
            )

        english_text = translation.translated_text or original_text
        # Trust the translation service - don't override with glossary
        if len(english_text) > 500:
            logger.info(
                "Translated text exceeded 500 characters; truncating (len=%d).",
                len(english_text),
            )
            english_text = english_text[:500]

        return ProcessedQuery(
            english_text=english_text,
            original_text=original_text,
            lang_code=lang_code,
            was_translated=True,
        )

    async def _detect_google(self, text: str, timeout_seconds: float) -> Dict[str, object]:
        url = self.endpoints.get("detect_url")
        if not url:
            raise ValueError("Google detection URL not configured.")
        if self.api_key:
            url = f"{url}?key={self.api_key}"

        payload = {"q": text}
        response = await self._post_json(url, payload, timeout_seconds)
        detections = response.get("data", {}).get("detections", [])
        if not detections or not detections[0]:
            raise ValueError("No detections returned from Google API.")
        detection = detections[0][0]
        return {
            "lang_code": detection.get("language"),
            "confidence": detection.get("confidence"),
        }

    async def _detect_googletrans(self, text: str) -> Dict[str, object]:
        def _execute() -> Dict[str, object]:
            client = self._get_googletrans_client()
            detection = client.detect(text)
            return {
                "lang_code": getattr(detection, "lang", None),
                "confidence": getattr(detection, "confidence", 0.0),
            }

        return await asyncio.to_thread(_execute)

    async def _detect_deepl(self, text: str, timeout_seconds: float) -> Dict[str, object]:
        url = self.endpoints.get("translate_url")
        if not url:
            raise ValueError("DeepL translate URL not configured.")

        payload = {"text": [text], "target_lang": "EN"}
        if self.api_key:
            payload["auth_key"] = self.api_key

        response = await self._post_json(url, payload, timeout_seconds)
        translations = response.get("translations", [])
        if not translations:
            raise ValueError("No detections returned from DeepL API.")
        detection = translations[0]
        return {
            "lang_code": detection.get("detected_source_language"),
            "confidence": 0.0,
        }

    async def _translate_google(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        timeout_seconds: float,
    ) -> str:
        url = self.endpoints.get("translate_url")
        if not url:
            raise ValueError("Google translate URL not configured.")
        if self.api_key:
            url = f"{url}?key={self.api_key}"

        payload = {"q": text, "target": target_lang}
        if source_lang and source_lang != "auto":
            payload["source"] = source_lang
        response = await self._post_json(url, payload, timeout_seconds)
        translations = response.get("data", {}).get("translations", [])
        if not translations:
            raise ValueError("No translations returned from Google API.")
        return translations[0].get("translatedText", "").strip()

    async def _translate_googletrans(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> str:
        def _execute() -> str:
            client = self._get_googletrans_client()
            if source_lang and source_lang != "auto":
                result = client.translate(text, src=source_lang, dest=target_lang)
            else:
                result = client.translate(text, dest=target_lang)
            return str(result.text).strip()

        return await asyncio.to_thread(_execute)

    async def _translate_deepl(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        timeout_seconds: float,
    ) -> str:
        url = self.endpoints.get("translate_url")
        if not url:
            raise ValueError("DeepL translate URL not configured.")

        payload = {"text": [text], "target_lang": target_lang.upper()}
        if source_lang and source_lang != "auto":
            payload["source_lang"] = source_lang.upper()
        if self.api_key:
            payload["auth_key"] = self.api_key

        response = await self._post_json(url, payload, timeout_seconds)
        translations = response.get("translations", [])
        if not translations:
            raise ValueError("No translations returned from DeepL API.")
        return str(translations[0].get("text", "")).strip()

    def _get_googletrans_client(self):
        if self._googletrans_client is None:
            try:
                from googletrans import Translator
            except ImportError as exc:
                raise RuntimeError(
                    "googletrans is not installed. Add it to requirements."
                ) from exc

            self._googletrans_client = Translator()

        return self._googletrans_client

    def _is_non_textual(self, text: str) -> bool:
        stripped = "".join(text.split())
        if not stripped:
            return True
        return not any(char.isalnum() for char in stripped)

    def _contains_non_ascii_letters(self, text: str) -> bool:
        """Check if text contains non-ASCII alphabetic characters."""
        return any(char.isalpha() and not char.isascii() for char in text)

    def _infer_language_from_characters(self, text: str) -> Optional[str]:
        """
        Infer language from Unicode character ranges.

        Returns language code if confidently inferred, None otherwise.
        Focuses on Vietnamese and other common non-ASCII languages.
        """
        # Vietnamese-specific diacritics and characters
        vietnamese_lower = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
        vietnamese_upper = "".join(c.upper() if c != "đ" else "Đ" for c in vietnamese_lower)
        vietnamese_chars = set(vietnamese_lower + vietnamese_upper)

        # Chinese character ranges (CJK Unified Ideographs)
        def is_chinese(char: str) -> bool:
            code = ord(char)
            return (0x4E00 <= code <= 0x9FFF or  # CJK Unified Ideographs
                    0x3400 <= code <= 0x4DBF or  # CJK Extension A
                    0x20000 <= code <= 0x2A6DF)  # CJK Extension B

        # Japanese Hiragana and Katakana
        def is_japanese_kana(char: str) -> bool:
            code = ord(char)
            return (0x3040 <= code <= 0x309F or  # Hiragana
                    0x30A0 <= code <= 0x30FF)    # Katakana

        # Korean Hangul
        def is_korean(char: str) -> bool:
            code = ord(char)
            return (0xAC00 <= code <= 0xD7AF or  # Hangul Syllables
                    0x1100 <= code <= 0x11FF)    # Hangul Jamo

        # Thai
        def is_thai(char: str) -> bool:
            code = ord(char)
            return 0x0E00 <= code <= 0x0E7F

        # Count character types
        viet_count = sum(1 for c in text if c in vietnamese_chars)
        chinese_count = sum(1 for c in text if is_chinese(c))
        japanese_count = sum(1 for c in text if is_japanese_kana(c))
        korean_count = sum(1 for c in text if is_korean(c))
        thai_count = sum(1 for c in text if is_thai(c))

        counts = {
            "vi": viet_count,
            "zh": chinese_count,
            "ja": japanese_count + chinese_count // 2,  # Japanese often uses kanji
            "ko": korean_count,
            "th": thai_count,
        }

        # Return the language with the most characteristic characters
        max_lang, max_count = max(counts.items(), key=lambda x: x[1])
        if max_count > 0:
            return max_lang

        return None

    def _extract_dominant_text(self, text: str) -> str:
        ascii_letters = [char for char in text if char.isascii() and char.isalpha()]
        non_ascii_letters = [char for char in text if not char.isascii() and char.isalpha()]
        if ascii_letters and non_ascii_letters:
            if len(ascii_letters) >= len(non_ascii_letters):
                return "".join(ascii_letters)
            return "".join(non_ascii_letters)
        return text

    def _apply_vietnamese_glossary(self, text: str) -> str:
        lowered = text.lower()
        sound_hint = any(marker in lowered for marker in self._VI_SOUND_MARKERS)
        cleaned = lowered

        for marker in self._VI_SOUND_MARKERS:
            cleaned = cleaned.replace(marker, " ")

        for vietnamese, english in self._VI_GLOSSARY:
            cleaned = cleaned.replace(vietnamese, english)

        cleaned = " ".join(cleaned.split())
        if sound_hint:
            cleaned = f"sound of {cleaned}".strip()

        return cleaned

    def _should_use_glossary(self, translated_text: str, glossary_hint: str) -> bool:
        if not glossary_hint:
            return False

        translated_lower = translated_text.lower()
        glossary_lower = glossary_hint.lower()

        translated_hits = any(keyword in translated_lower for keyword in self._VI_KEYWORDS)
        glossary_hits = any(keyword in glossary_lower for keyword in self._VI_KEYWORDS)

        if glossary_hits and not translated_hits:
            logger.info("Using Vietnamese glossary fallback for translation: %s", glossary_hint)
            return True

        return False

    def _build_translation_warning(self, error_msg: Optional[str]) -> str:
        if error_msg and "rate limit" in error_msg.lower():
            return "Translation rate limit reached. Searching with original text may yield less accurate results."
        if error_msg and (
            "http error 503" in error_msg.lower()
            or "service unavailable" in error_msg.lower()
            or "timeout" in error_msg.lower()
            or "failed" in error_msg.lower()
        ):
            return "Translation unavailable. Searching with original text may yield less accurate results."
        return "Translation unavailable. Searching with original text may yield less accurate results."

    def _get_cached_translation(self, key: tuple[str, str, str]) -> Optional[str]:
        now = time.time()
        entry = self._translation_cache.get(key)
        if not entry:
            logger.info("Translation cache miss")
            return None
        value, timestamp = entry
        if now - timestamp > self._cache_ttl_seconds:
            self._translation_cache.pop(key, None)
            logger.info("Translation cache expired")
            return None
        self._translation_cache.move_to_end(key)
        logger.info("Translation cache hit")
        return value

    def _set_cached_translation(self, key: tuple[str, str, str], value: str) -> None:
        self._translation_cache[key] = (value, time.time())
        self._translation_cache.move_to_end(key)
        while len(self._translation_cache) > self._cache_max_size:
            self._translation_cache.popitem(last=False)

    def _get_cached_detection(self, text: str) -> Optional[LanguageDetectionResult]:
        now = time.time()
        entry = self._language_cache.get(text)
        if not entry:
            logger.info("Language detection cache miss")
            return None
        value, timestamp = entry
        if now - timestamp > self._cache_ttl_seconds:
            self._language_cache.pop(text, None)
            logger.info("Language detection cache expired")
            return None
        self._language_cache.move_to_end(text)
        logger.info("Language detection cache hit")
        return value

    def _set_cached_detection(self, text: str, value: LanguageDetectionResult) -> None:
        self._language_cache[text] = (value, time.time())
        self._language_cache.move_to_end(text)
        while len(self._language_cache) > self._cache_max_size:
            self._language_cache.popitem(last=False)

    async def _post_json(
        self, url: str, payload: Dict[str, object], timeout_seconds: float
    ) -> Dict[str, object]:
        headers = {"Content-Type": "application/json"}
        data = json.dumps(payload).encode("utf-8")

        def _execute() -> Dict[str, object]:
            request = urlrequest.Request(url, data=data, headers=headers, method="POST")
            with urlrequest.urlopen(request, timeout=timeout_seconds) as response:
                body = response.read().decode("utf-8")
            return json.loads(body)

        try:
            return await asyncio.to_thread(_execute)
        except urlerror.HTTPError as exc:
            raise RuntimeError(f"HTTP Error {exc.code}: {exc.reason}") from exc
        except urlerror.URLError as exc:
            raise RuntimeError(f"Translation API request failed: {exc}") from exc
