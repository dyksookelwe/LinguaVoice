from pathlib import Path

from app.providers.cloning import clone_speech
from app.providers.tts import synthesize_speech
from app.schemas.segment import Segment


def synthesize_segment(
    segment: Segment,
    reference_wav: Path,
    use_cloning: bool = True,
) -> Path:
    """Generate Slovak audio for one segment. Cloning vs TTS is our switch."""
    if use_cloning:
        return clone_speech(segment.sk_text, reference_wav, language="sk")
    return synthesize_speech(segment.sk_text, language="sk")
