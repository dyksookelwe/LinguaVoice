import wave
from pathlib import Path

import pytest

from app.audio.align import align_segment
from app.schemas.segment import Segment


def write_wav(path: Path, seconds: float, rate: int = 24000) -> Path:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * int(seconds * rate))
    return path


def make_segment(tmp_path: Path, src: float, gen: float) -> Segment:
    audio = write_wav(tmp_path / "seg-1.wav", gen)
    return Segment(
        id="seg-1", start=0.0, end=src, src_duration=src,
        gen_duration=gen, audio_path=str(audio),
    )


def test_within_range_is_stretched_to_window(tmp_path):
    seg = make_segment(tmp_path, src=1.0, gen=1.05)
    align_segment(seg)
    assert seg.stretch_ratio == pytest.approx(1.05)
    assert seg.audio_path.endswith("seg-1_aligned.wav")
    assert Path(seg.audio_path).exists()
    assert (tmp_path / "seg-1.wav").exists()  # оригинал не удаляем
    assert seg.gen_duration == pytest.approx(1.0, abs=0.05)


def test_too_long_is_left_alone_but_ratio_recorded(tmp_path):
    seg = make_segment(tmp_path, src=1.0, gen=1.5)
    original = seg.audio_path
    align_segment(seg)
    assert seg.audio_path == original
    assert seg.gen_duration == pytest.approx(1.5)
    assert seg.stretch_ratio == pytest.approx(1.5)


def test_too_short_is_left_alone_but_ratio_recorded(tmp_path):
    seg = make_segment(tmp_path, src=2.0, gen=1.0)
    original = seg.audio_path
    align_segment(seg)
    assert seg.audio_path == original
    assert seg.stretch_ratio == pytest.approx(0.5)


def test_tiny_difference_is_not_processed(tmp_path):
    seg = make_segment(tmp_path, src=1.0, gen=1.01)
    original = seg.audio_path
    align_segment(seg)
    assert seg.audio_path == original
    assert seg.stretch_ratio == pytest.approx(1.01)


def test_segment_without_audio_is_unchanged():
    seg = Segment(id="seg-1", start=0.0, end=1.0, src_duration=1.0)
    align_segment(seg)
    assert seg.stretch_ratio == 1.0
    assert seg.audio_path is None