import json

import pytest

from app.schemas.job import Job
from app.schemas.segment import Segment
from app.services.metrics import compute_metrics, write_metrics


def make_job() -> Job:
    return Job(
        id="j",
        source_path="x",
        segments=[
            Segment(id="a", start=0.0, end=1.0, gen_duration=1.0,
                    placed_start=0.0, voice="clone"),
            Segment(id="b", start=2.0, end=3.0, gen_duration=1.5,
                    placed_start=2.75, voice="fallback"),
        ],
    )


def test_max_delay_and_voice_share():
    m = compute_metrics(make_job())
    assert m.max_delay_seconds == pytest.approx(0.75)
    assert m.clone_segment_ratio == pytest.approx(0.5)


def test_no_segments_gives_zeros():
    m = compute_metrics(Job(id="j", source_path="x"))
    assert m.max_delay_seconds == 0.0
    assert m.clone_segment_ratio == 0.0


def test_write_metrics_json(tmp_path):
    path = write_metrics(compute_metrics(make_job(), pipeline_seconds=3.2),
                         tmp_path / "metrics.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["pipeline_seconds"] == pytest.approx(3.2)
    assert "max_delay_seconds" in data