from pathlib import Path

from app.audio.validate import ValidatedAudio


def convert_to_wav(audio: ValidatedAudio) -> Path:
    """Convert a validated file to mono 16 kHz WAV. Implemented in stage 1."""
    raise NotImplementedError("convert_to_wav is implemented in stage 1")
