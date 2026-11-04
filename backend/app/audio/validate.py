from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ValidatedAudio:
    path: Path
    duration_seconds: float
    sample_rate: int
    channels: int


def validate_audio(path: Path) -> ValidatedAudio:
    """Check format, size, and duration. Implemented in stage 1."""
    raise NotImplementedError("validate_audio is implemented in stage 1")
