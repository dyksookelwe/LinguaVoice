from pathlib import Path

from app.schemas.segment import Segment


def assemble_track(segments: list[Segment], reference_wav: Path) -> Path:
    """Join aligned segments using original pause boundaries."""
    raise NotImplementedError("assemble_track is implemented in stage 6")
