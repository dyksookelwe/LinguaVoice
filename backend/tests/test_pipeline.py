import wave
from pathlib import Path

import pytest

from app.schemas.job import Job, JobStatus
from app.schemas.segment import Segment
from app.services.metrics import compute_metrics
from app.services.pipeline import run_pipeline


def test_run_pipeline_is_a_function_chain(tmp_path: Path, monkeypatch) -> None:
    wav_path = tmp_path / "sample.wav"
    with wave.open(str(wav_path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(b"\x00\x00" * 16000)

    # подставляем слова вместо настоящей модели: тест не должен грузить Whisper
    monkeypatch.setattr(
        "app.services.transcribe.transcribe_words",
        lambda path: [{"text": "Ahoj", "start": 0.0, "end": 1.0}],
    )
    monkeypatch.setattr(
        "app.services.translate.translate_sk_to_en", lambda text: "Hello"
    )
    def fake_clone(text, reference_wav, output_path, language="en"):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(output_path), "wb") as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(24000)
            out.writeframes(b"\x00\x00" * 24000)
        return output_path

    monkeypatch.setattr("app.services.synthesize.clone_speech", fake_clone)

    job: Job = Job(id="job-1", source_path=str(wav_path))

    result = run_pipeline(job)

    assert result.status == JobStatus.done
    assert Path(result.output_path).exists()
    assert result.metrics.source_duration > 0
    assert result.segments[0].voice == "clone"
    assert Path(result.output_mp3_path).exists()
    assert (Path(result.output_path).parent / "metrics.json").exists()


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