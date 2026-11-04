from pathlib import Path

import pytest

from app.schemas.job import Job, JobStatus
from app.services.metrics import compute_metrics
from app.services.pipeline import run_pipeline
from app.schemas.segment import Segment


def test_run_pipeline_is_a_function_chain(tmp_path: Path) -> None:
    job = Job(id="job-1", source_path=str(tmp_path / "sample.wav"))
    with pytest.raises(NotImplementedError, match="stage 1"):
        run_pipeline(job)
    assert job.status == JobStatus.failed


def test_compute_metrics_from_segment_fields() -> None:
    job = Job(
        id="job-2",
        source_path="sample.wav",
        segments=[
            Segment(
                id="s1",
                start=0.0,
                end=1.0,
                src_duration=1.0,
                gen_duration=1.05,
                stretch_ratio=1.05,
            ),
            Segment(
                id="s2",
                start=1.2,
                end=2.2,
                src_duration=1.0,
                gen_duration=1.4,
                stretch_ratio=1.4,
            ),
        ],
    )
    metrics = compute_metrics(job, pipeline_seconds=3.2)
    assert metrics.source_duration == pytest.approx(2.2)
    assert metrics.dubbed_duration == pytest.approx(2.45)
    assert metrics.overstretched_segment_ratio == pytest.approx(0.5)
    assert metrics.pipeline_seconds == pytest.approx(3.2)
