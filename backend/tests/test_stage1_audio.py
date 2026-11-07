import wave
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.config as config
from app.audio.convert import convert_to_wav
from app.audio.validate import (
    AudioTooLongError,
    FileTooLargeError,
    InvalidAudioError,
    validate_audio,
)
from app.main import app

MODULES = ("app.audio.validate", "app.services.storage", "app.api.jobs")


@pytest.fixture(autouse=True)
def settings_override(monkeypatch, tmp_path):
    """Подменяет настройки на время теста; загрузки идут во временную папку."""
    state = {"upload_dir": str(tmp_path / "uploads")}

    def apply(**changes):
        state.update(changes)
        s = replace(config.get_settings(), **state)
        for mod in MODULES:
            monkeypatch.setattr(f"{mod}.get_settings", lambda s=s: s)

    apply()
    return apply


def make_wav(path: Path, seconds: float = 1.0, rate: int = 44100, channels: int = 2) -> Path:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * channels * int(seconds * rate))
    return path


def test_valid_wav(tmp_path):
    audio = validate_audio(make_wav(tmp_path / "a.wav", seconds=2))
    assert audio.duration_seconds == pytest.approx(2, abs=0.1)
    assert audio.channels == 2
    assert audio.sample_rate == 44100


def test_too_long(tmp_path, settings_override):
    settings_override(max_duration_seconds=1)
    with pytest.raises(AudioTooLongError):
        validate_audio(make_wav(tmp_path / "a.wav", seconds=2))


def test_too_large(tmp_path, settings_override):
    settings_override(max_upload_mb=1)
    with pytest.raises(FileTooLargeError):
        validate_audio(make_wav(tmp_path / "a.wav", seconds=6))


def test_empty_file(tmp_path):
    p = tmp_path / "a.wav"
    p.write_bytes(b"")
    with pytest.raises(InvalidAudioError):
        validate_audio(p)


def test_garbage_with_wav_extension(tmp_path):
    p = tmp_path / "a.wav"
    p.write_bytes(b"this is definitely not audio" * 100)
    with pytest.raises(InvalidAudioError):
        validate_audio(p)


def test_wrong_extension(tmp_path):
    p = make_wav(tmp_path / "a.wav")
    renamed = p.rename(tmp_path / "a.txt")
    with pytest.raises(InvalidAudioError):
        validate_audio(renamed)


def test_convert_to_mono_16k(tmp_path):
    audio = validate_audio(make_wav(tmp_path / "a.wav", seconds=1, rate=44100, channels=2))
    converted = validate_audio(convert_to_wav(audio))
    assert converted.sample_rate == 16000
    assert converted.channels == 1


client = TestClient(app)


def post_file(path: Path):
    with path.open("rb") as f:
        return client.post("/jobs", files={"file": (path.name, f, "audio/wav")})


def test_api_accepts_valid_file(tmp_path):
    r = post_file(make_wav(tmp_path / "a.wav"))
    assert r.status_code == 201
    assert r.json()["status"] == "queued"


def test_api_rejects_garbage_and_cleans_up(tmp_path):
    bad = tmp_path / "bad.wav"
    bad.write_bytes(b"nope" * 1000)
    r = post_file(bad)
    assert r.status_code == 422
    uploads = tmp_path / "uploads"
    assert not uploads.exists() or not any(uploads.iterdir())


def test_api_rejects_too_long(tmp_path, settings_override):
    settings_override(max_duration_seconds=1)
    assert post_file(make_wav(tmp_path / "a.wav", seconds=2)).status_code == 422


def test_api_rejects_too_large(tmp_path, settings_override):
    settings_override(max_upload_mb=1)
    assert post_file(make_wav(tmp_path / "a.wav", seconds=6)).status_code == 413