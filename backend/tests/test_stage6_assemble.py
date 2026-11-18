import wave
from pathlib import Path

import pytest

from app.audio.export import assemble_track, export_mp3
from app.audio.validate import validate_audio
from app.schemas.segment import Segment

RATE = 24000


def write_wav(path: Path, seconds: float) -> Path:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"\x00\x00" * int(seconds * RATE))
    return path


def make_segment(tmp_path: Path, name: str, start: float, gen: float) -> Segment:
    audio = write_wav(tmp_path / f"{name}.wav", gen)
    return Segment(
        id=name, start=start, end=start + gen, gen_duration=gen, audio_path=str(audio)
    )


def duration(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


def test_segments_placed_at_original_times(tmp_path):
    a = make_segment(tmp_path, "a", 0.0, 1.0)
    b = make_segment(tmp_path, "b", 3.0, 1.0)
    out = assemble_track([b, a], tmp_path / "reference.wav")  # порядок не важен
    assert duration(out) == pytest.approx(4.0)
    assert b.placed_start == pytest.approx(3.0)


def test_overflowing_segment_shifts_the_next_one(tmp_path):
    a = make_segment(tmp_path, "a", 0.0, 2.0)
    b = make_segment(tmp_path, "b", 1.0, 1.0)
    out = assemble_track([a, b], tmp_path / "reference.wav")
    assert b.placed_start == pytest.approx(2.0)  # сдвинут на 1 с
    assert duration(out) == pytest.approx(3.0)


def test_leading_silence_is_kept(tmp_path):
    a = make_segment(tmp_path, "a", 0.5, 1.0)
    out = assemble_track([a], tmp_path / "reference.wav")
    assert a.placed_start == pytest.approx(0.5)
    assert duration(out) == pytest.approx(1.5)


def test_no_segments_is_an_error(tmp_path):
    with pytest.raises(ValueError):
        assemble_track([], tmp_path / "reference.wav")


def test_export_mp3(tmp_path):
    wav = write_wav(tmp_path / "dubbed.wav", 1.0)
    mp3 = export_mp3(wav)
    assert mp3.suffix == ".mp3"
    assert validate_audio(mp3).duration_seconds == pytest.approx(1.0, abs=0.2)