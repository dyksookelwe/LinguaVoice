import json
from pathlib import Path

from app.schemas.job import Job
from app.schemas.metrics import Metrics
from app.schemas.segment import Segment

OVERSTRETCH_MIN = 0.9
OVERSTRETCH_MAX = 1.1


def compute_metrics(job: Job, pipeline_seconds: float = 0.0) -> Metrics:
    """Compute duration ratio, overstretch share, delay and voice share."""
    segments = job.segments
    source_duration = _source_duration(segments)
    dubbed_duration = sum(segment.gen_duration for segment in segments)
    duration_ratio = (
        dubbed_duration / source_duration if source_duration > 0 else 0.0
    )
    overstretched = sum(
        1
        for segment in segments
        if segment.stretch_ratio < OVERSTRETCH_MIN
        or segment.stretch_ratio > OVERSTRETCH_MAX
    )
    count = len(segments)
    max_delay = max(
        (max(0.0, s.placed_start - s.start) for s in segments), default=0.0
    )
    cloned = sum(1 for s in segments if s.voice == "clone")
    return Metrics(
        pipeline_seconds=pipeline_seconds,
        source_duration=source_duration,
        dubbed_duration=dubbed_duration,
        duration_ratio=duration_ratio,
        overstretched_segment_ratio=overstretched / count if count else 0.0,
        max_delay_seconds=max_delay,
        clone_segment_ratio=cloned / count if count else 0.0,
    )


def write_metrics(metrics: Metrics, path: Path) -> Path:
    """Save metrics as JSON (all numbers are computed by our code)."""
    path.write_text(
        json.dumps(metrics.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def _source_duration(segments: list[Segment]) -> float:
    if not segments:
        return 0.0
    return max(segment.end for segment in segments) - min(
        segment.start for segment in segments
    )