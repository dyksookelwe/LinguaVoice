import shutil
import subprocess
from pathlib import Path

from app.audio.validate import ValidatedAudio
from app.config import get_settings


def convert_to_wav(audio: ValidatedAudio) -> Path:
    """Convert a validated file to mono 16 kHz WAV."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg не найден: установите его и добавьте в PATH")
    settings = get_settings()
    dst = audio.path.parent / "reference.wav"
    result = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(audio.path),
         "-ac", "1", "-ar", str(settings.sample_rate),
         "-c:a", "pcm_s16le", str(dst)],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg не смог сконвертировать файл: {result.stderr[-300:]}")
    return dst