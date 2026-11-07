from app.providers.translation import translate_sk_to_en


def translate_segment(src_text: str, src_duration: float) -> str:
    """Translate one segment and apply length checks against src_duration."""
    _translated = translate_sk_to_en(src_text)
    _ = src_duration
    raise NotImplementedError("translate_segment is implemented in stage 4")
