import logging
from pathlib import Path

from app.audio.validate import validate_audio
from app.config import get_settings
from app.providers.cloning import clone_speech
from app.providers.tts import synthesize_speech
from app.schemas.segment import Segment

logger = logging.getLogger(__name__)

LANGUAGE = "en"


def synthesize_segment(
    segment: Segment,
    reference_wav: Path,
    use_cloning: bool = True,
) -> Path:
    """Generate English audio for one segment. Cloning vs TTS is our switch."""
    text = segment.tgt_text.strip()
    if not text:
        raise ValueError(f"У сегмента {segment.id} нет переведённого текста")

    output_path = reference_wav.parent / "segments" / f"{segment.id}.wav"

    wants_clone = (
        use_cloning and get_settings().cloning_enabled and reference_wav.exists()
    )
    if wants_clone:
        try:
            clone_speech(text, reference_wav, output_path, language=LANGUAGE)
            segment.voice = "clone"
        except Exception:
            logger.warning(
                "Клонирование не удалось для %s, берём запасной голос",
                segment.id,
                exc_info=True,
            )
            synthesize_speech(text, output_path, language=LANGUAGE)
            segment.voice = "fallback"
    else:
        synthesize_speech(text, output_path, language=LANGUAGE)
        segment.voice = "fallback"

    segment.gen_duration = validate_audio(output_path).duration_seconds
    return output_path