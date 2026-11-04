from pathlib import Path
from typing import TypedDict


class WordTimestamp(TypedDict):
    text: str
    start: float
    end: float


def transcribe_words(wav_path: Path) -> list[WordTimestamp]:
    """Return words with timestamps from the ASR model. No segmentation logic."""
    raise NotImplementedError("ASR adapter is implemented in stage 3")
