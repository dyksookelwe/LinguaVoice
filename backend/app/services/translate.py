import re

from app.config import get_settings
from app.providers.translation import translate_sk_to_en


def normalize_text(text: str) -> str:
    """Убирает лишние пробелы и пробелы перед знаками препинания."""
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"\s+([,.;:!?])", r"\1", text)


def estimate_speech_seconds(text: str) -> float:
    """Грубая оценка длительности озвучки по числу символов."""
    return len(text) / get_settings().tts_chars_per_sec


def is_text_too_long(tgt_text: str, src_duration: float) -> bool:
    """Флаг «текст длиннее окна»: оценка озвучки не влезает в исходный отрезок."""
    if not tgt_text or src_duration <= 0:
        return False
    limit = src_duration * get_settings().length_tolerance
    return estimate_speech_seconds(tgt_text) > limit


def translate_segment(src_text: str, src_duration: float) -> str:
    """Translate one segment (SK -> EN) through the engine and normalize it."""
    # src_duration пока не используется: оставлена по сигнатуре плана
    return normalize_text(translate_sk_to_en(normalize_text(src_text)))