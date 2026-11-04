from pathlib import Path

from app.providers.asr import transcribe_words
from app.schemas.segment import Segment


def transcribe_and_segment(wav_path: Path) -> list[Segment]:
    """Turn ASR timestamps into segments using pause and length rules."""
    _words = transcribe_words(wav_path)
    raise NotImplementedError("transcribe_and_segment is implemented in stage 3")
