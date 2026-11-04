from app.schemas.segment import Segment

MIN_STRETCH_RATIO = 0.9
MAX_STRETCH_RATIO = 1.1


def align_segment(segment: Segment) -> Segment:
    """Fit generated audio to the source window without extreme stretching."""
    raise NotImplementedError("align_segment is implemented in stage 6")
