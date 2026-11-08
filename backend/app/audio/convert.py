import shutil
import subprocess
from pathlib import Path

from app.audio.validate import ValidatedAudio
from app.config import get_settings


def _to_mono_wav(src: Path, dst: Path, sample_rate: int) -> Path:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg не найден: установите его и добавьте в PATH")
    result = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(src),
         "-ac", "1", "-ar", str(sample_rate),
         "-c:a", "pcm_s16le", str(dst)],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg не смог сконвертировать файл: {result.stderr[-300:]}")
    return dst


def convert_to_wav(audio: ValidatedAudio) -> Path:
    """Convert a validated file to mono 16 kHz WAV (for ASR)."""
    return _to_mono_wav(
        audio.path, audio.path.parent / "reference.wav", get_settings().sample_rate
    )


def make_voice_reference(audio: ValidatedAudio) -> Path:
    """Mono 24 kHz WAV: the voice sample for cloning (XTTS works at 24 kHz)."""
    return _to_mono_wav(
        audio.path,
        audio.path.parent / "voice_reference.wav",
        get_settings().voice_sample_rate,
    )