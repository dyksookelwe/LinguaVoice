import json
import wave
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.config as config
from app.main import app
from app.schemas.job import Job, JobStatus
from app.schemas.metrics import Metrics
from app.schemas.segment import Segment
from app.services.jobs import needs_review

MODULES = ("app.audio.validate", "app.services.storage", "app.api.jobs")


@pytest.fixture(autouse=True)
def isolated_uploads(monkeypatch, tmp_path):
    s = replace(config.get_settings(), upload_dir=str(tmp_path / "uploads"))
    for mod in MODULES:
        monkeypatch.setattr(f"{mod}.get_settings", lambda s=s: s)


# TestClient дожидается фоновых задач, поэтому после POST задача уже обработана
client = TestClient(app)


def make_wav(path: Path, seconds: float = 1.0, rate: int = 44100) -> Path:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * int(seconds * rate))
    return path


def upload(tmp_path: Path):
    wav = make_wav(tmp_path / "a.wav")
    with wav.open("rb") as f:
        return client.post("/jobs", files={"file": ("a.wav", f, "audio/wav")})


def fake_pipeline(stretch: float = 1.0, too_long: bool = False, fail: bool = False):
    def run(job: Job) -> Job:
        job.status = JobStatus.processing
        if fail:
            job.status = JobStatus.failed
            job.error = "boom"
            raise RuntimeError("boom")
        folder = Path(job.source_path).parent
        wav, mp3 = folder / "dubbed.wav", folder / "dubbed.mp3"
        wav.write_bytes(b"RIFFwav")
        mp3.write_bytes(b"ID3mp3")
        job.output_path, job.output_mp3_path = str(wav), str(mp3)
        job.segments = [
            Segment(
                id="seg-1", start=0.0, end=2.0, src_text="Ahoj", tgt_text="Hello",
                src_duration=2.0, gen_duration=2.0, stretch_ratio=stretch,
                text_too_long=too_long, voice="clone",
            )
        ]
        job.metrics = Metrics(source_duration=2.0)
        job.status = JobStatus.done
        return job

    return run


def use_pipeline(monkeypatch, **kwargs):
    monkeypatch.setattr("app.services.jobs.run_pipeline", fake_pipeline(**kwargs))


def test_job_runs_in_background_and_is_readable(tmp_path, monkeypatch):
    use_pipeline(monkeypatch)
    r = upload(tmp_path)
    assert r.status_code == 201
    assert r.json()["status"] == "queued"
    body = client.get(f"/jobs/{r.json()['job_id']}").json()
    assert body["status"] == "done"
    assert body["segments"][0]["tgt_text"] == "Hello"
    assert body["metrics"]["source_duration"] == 2.0
    assert body["audio_ready"] is True
    text = json.dumps(body)
    for secret in ("source_path", "output_path", "audio_path"):
        assert secret not in text


def test_needs_review_when_stretch_out_of_range(tmp_path, monkeypatch):
    use_pipeline(monkeypatch, stretch=1.3)
    job_id = upload(tmp_path).json()["job_id"]
    assert client.get(f"/jobs/{job_id}").json()["status"] == "needs_review"


def test_failed_job_reports_error(tmp_path, monkeypatch):
    use_pipeline(monkeypatch, fail=True)
    job_id = upload(tmp_path).json()["job_id"]
    body = client.get(f"/jobs/{job_id}").json()
    assert body["status"] == "failed"
    assert body["error"] == "boom"
    assert body["audio_ready"] is False


def test_download_mp3_and_wav(tmp_path, monkeypatch):
    use_pipeline(monkeypatch)
    job_id = upload(tmp_path).json()["job_id"]
    mp3 = client.get(f"/jobs/{job_id}/audio")
    assert mp3.status_code == 200 and mp3.content == b"ID3mp3"
    assert mp3.headers["content-type"] == "audio/mpeg"
    wav = client.get(f"/jobs/{job_id}/audio?format=wav")
    assert wav.status_code == 200 and wav.content == b"RIFFwav"
    assert client.get(f"/jobs/{job_id}/audio?format=ogg").status_code == 422


def test_audio_not_ready_is_409(tmp_path, monkeypatch):
    monkeypatch.setattr("app.api.jobs.run_job", lambda job_id: None)
    job_id = upload(tmp_path).json()["job_id"]
    assert client.get(f"/jobs/{job_id}").json()["status"] == "queued"
    assert client.get(f"/jobs/{job_id}/audio").status_code == 409


def test_original_download(tmp_path, monkeypatch):
    monkeypatch.setattr("app.api.jobs.run_job", lambda job_id: None)
    job_id = upload(tmp_path).json()["job_id"]
    r = client.get(f"/jobs/{job_id}/original")
    assert r.status_code == 200 and len(r.content) > 0


def test_unknown_job_is_404():
    assert client.get("/jobs/nope").status_code == 404
    assert client.get("/jobs/nope/audio").status_code == 404
    assert client.get("/jobs/nope/original").status_code == 404


def test_needs_review_rule():
    ok = Segment(id="a", start=0, end=1, stretch_ratio=1.05)
    long_text = Segment(id="b", start=0, end=1, text_too_long=True)
    stretched = Segment(id="c", start=0, end=1, stretch_ratio=0.8)
    assert needs_review(Job(id="j", source_path="x", segments=[ok])) is False
    assert needs_review(Job(id="j", source_path="x", segments=[ok, long_text])) is True
    assert needs_review(Job(id="j", source_path="x", segments=[stretched])) is True