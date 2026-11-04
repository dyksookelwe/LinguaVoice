from app.providers.translation import translate_en_to_sk


def translate_segment(en_text: str, src_duration: float) -> str:
    """Translate one segment and apply length checks against src_duration."""
    _translated = translate_en_to_sk(en_text)
    _ = src_duration
    raise NotImplementedError("translate_segment is implemented in stage 4")
