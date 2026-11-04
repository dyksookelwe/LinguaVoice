from app.schemas.job import Job
from app.schemas.metrics import Metrics
from app.schemas.segment import Segment

OVERSTRETCH_MIN = 0.9
OVERSTRETCH_MAX = 1.1


def compute_metrics(job: Job, pipeline_seconds: float = 0.0) -> Metrics:
    """Compute duration ratio and overstretch share from segment fields."""
    source_duration = _source_duration(job.segments)
    dubbed_duration = sum(segment.gen_duration for segment in job.segments)
    duration_ratio = (
        dubbed_duration / source_duration if source_duration > 0 else 0.0
    )
    overstretched = 0
    if job.segments:
        overstretched = sum(
            1
            for segment in job.segments
            if segment.stretch_ratio < OVERSTRETCH_MIN
            or segment.stretch_ratio > OVERSTRETCH_MAX
        )
    overstretched_ratio = (
        overstretched / len(job.segments) if job.segments else 0.0
    )
    return Metrics(
        pipeline_seconds=pipeline_seconds,
        source_duration=source_duration,
        dubbed_duration=dubbed_duration,
        duration_ratio=duration_ratio,
        overstretched_segment_ratio=overstretched_ratio,
    )


def _source_duration(segments: list[Segment]) -> float:
    if not segments:
        return 0.0
    return max(segment.end for segment in segments) - min(
        segment.start for segment in segments
    )
