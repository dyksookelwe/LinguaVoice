import shutil
import subprocess
from pathlib import Path

from app.audio.validate import validate_audio
from app.schemas.segment import Segment

MIN_STRETCH_RATIO = 0.9
MAX_STRETCH_RATIO = 1.1
NO_STRETCH_EPS = 0.02  # разницу меньше 2 % не трогаем: на слух незаметна


def _change_tempo(src: Path, dst: Path, factor: float) -> Path:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg не найден: установите его и добавьте в PATH")
    result = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(src),
         "-filter:a", f"atempo={factor:.4f}", "-c:a", "pcm_s16le", str(dst)],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg не смог изменить темп: {result.stderr[-300:]}")
    return dst


def align_segment(segment: Segment) -> Segment:
    """Fit generated audio to the source window without extreme stretching."""
    if not segment.audio_path or segment.src_duration <= 0 or segment.gen_duration <= 0:
        return segment

    ratio = segment.gen_duration / segment.src_duration
    segment.stretch_ratio = ratio  # записываем всегда: из него считаются метрики

    if abs(ratio - 1.0) < NO_STRETCH_EPS:
        return segment
    if not (MIN_STRETCH_RATIO <= ratio <= MAX_STRETCH_RATIO):
        return segment  # слишком сильно: длительность оставляем, метрика отметит

    src = Path(segment.audio_path)
    dst = src.with_name(f"{src.stem}_aligned.wav")
    _change_tempo(src, dst, ratio)
    segment.audio_path = str(dst)
    segment.gen_duration = validate_audio(dst).duration_seconds
    return segment