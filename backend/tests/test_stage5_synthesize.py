import wave
from dataclasses import replace
from pathlib import Path

import pytest

import app.config as config
from app.schemas.segment import Segment
from app.services.synthesize import synthesize_segment


def write_wav(path: Path, seconds: float = 1.0, rate: int = 24000) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * int(seconds * rate))
    return path


@pytest.fixture
def setup(tmp_path, monkeypatch):
    reference = write_wav(tmp_path / "reference.wav")
    calls = []

    def fake_clone(text, reference_wav, output_path, language="en"):
        calls.append("clone")
        return write_wav(output_path)

    def fake_tts(text, output_path, language="en"):
        calls.append("tts")
        return write_wav(output_path)

    monkeypatch.setattr("app.services.synthesize.clone_speech", fake_clone)
    monkeypatch.setattr("app.services.synthesize.synthesize_speech", fake_tts)
    segment = Segment(id="seg-1", start=0.0, end=2.0, tgt_text="Hello there")
    return reference, segment, calls


def test_uses_clone_by_default(setup):
    reference, segment, calls = setup
    out = synthesize_segment(segment, reference)
    assert calls == ["clone"]
    assert segment.voice == "clone"
    assert out == reference.parent / "segments" / "seg-1.wav"
    assert segment.gen_duration == pytest.approx(1.0, abs=0.05)


def test_falls_back_when_clone_fails(setup, monkeypatch):
    reference, segment, calls = setup

    def broken_clone(text, reference_wav, output_path, language="en"):
        raise RuntimeError("model crashed")

    monkeypatch.setattr("app.services.synthesize.clone_speech", broken_clone)
    synthesize_segment(segment, reference)
    assert calls == ["tts"]
    assert segment.voice == "fallback"


def test_no_clone_when_disabled_by_argument(setup):
    reference, segment, calls = setup
    synthesize_segment(segment, reference, use_cloning=False)
    assert calls == ["tts"]
    assert segment.voice == "fallback"


def test_no_clone_when_disabled_in_settings(setup, monkeypatch):
    reference, segment, calls = setup
    s = replace(config.get_settings(), cloning_enabled=False)
    monkeypatch.setattr("app.services.synthesize.get_settings", lambda: s)
    synthesize_segment(segment, reference)
    assert calls == ["tts"]


def test_fallback_when_reference_missing(setup):
    reference, segment, calls = setup
    reference.unlink()
    synthesize_segment(segment, reference)
    assert calls == ["tts"]
    assert segment.voice == "fallback"


def test_empty_text_is_rejected(setup):
    reference, segment, _ = setup
    segment.tgt_text = "   "
    with pytest.raises(ValueError):
        synthesize_segment(segment, reference)