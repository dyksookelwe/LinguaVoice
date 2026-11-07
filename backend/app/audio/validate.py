import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from app.config import get_settings


class InvalidAudioError(Exception):
    """Файл не подходит как входное аудио"""


class FileTooLargeError(InvalidAudioError):
    pass


class AudioTooLongError(InvalidAudioError):
    pass


@dataclass(frozen=True)
class ValidatedAudio:
    path: Path
    duration_seconds: float
    sample_rate: int
    channels: int


_ALLOWED_FORMATS = {"mp3", "wav"}


def _probe(path: Path) -> dict:
    if shutil.which("ffprobe") is None:
        raise RuntimeError("ffprobe не найден: установите ffmpeg и добавьте его в PATH")
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_format", "-show_streams", str(path)],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise InvalidAudioError("Файл повреждён или не является аудио")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise InvalidAudioError("Не удалось прочитать метаданные файла") from exc


def validate_audio(path: Path) -> ValidatedAudio:
    """Check format, size, and duration."""
    settings = get_settings()

    if path.suffix.lower() not in settings.allowed_extensions:
        raise InvalidAudioError("Допустимы только файлы MP3 и WAV")

    size = path.stat().st_size
    if size == 0:
        raise InvalidAudioError("Файл пустой")
    if size > settings.max_upload_mb * 1024 * 1024:
        raise FileTooLargeError(f"Файл больше {settings.max_upload_mb} МБ")

    info = _probe(path)

    # реальный формат по содержимому, а не по расширению
    format_names = set(info.get("format", {}).get("format_name", "").split(","))
    if not format_names & _ALLOWED_FORMATS:
        raise InvalidAudioError("Содержимое файла не похоже на MP3 или WAV")

    stream = next(
        (s for s in info.get("streams", []) if s.get("codec_type") == "audio"), None
    )
    if stream is None:
        raise InvalidAudioError("В файле нет аудиодорожки")

    try:
        duration = float(info["format"]["duration"])
        sample_rate = int(stream["sample_rate"])
        channels = int(stream["channels"])
    except (KeyError, ValueError) as exc:
        raise InvalidAudioError("Не удалось определить параметры аудио") from exc

    if duration <= 0:
        raise InvalidAudioError("Нулевая длительность аудио")
    if duration > settings.max_duration_seconds:
        raise AudioTooLongError(
            f"Длительность {duration:.0f} с превышает лимит "
            f"{settings.max_duration_seconds} с"
        )

    return ValidatedAudio(path, duration, sample_rate, channels)