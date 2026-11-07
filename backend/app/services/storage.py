import shutil
import time
from pathlib import Path

from fastapi import UploadFile

from app.audio.validate import FileTooLargeError
from app.config import Settings, get_settings

_CHUNK = 1024 * 1024


def job_dir(job_id: str) -> Path:
    return Path(get_settings().upload_dir) / job_id


def create_job_dir(job_id: str) -> Path:
    directory = job_dir(job_id)
    directory.mkdir(parents=True, exist_ok=False)
    return directory


def remove_job_dir(job_id: str) -> None:
    shutil.rmtree(job_dir(job_id), ignore_errors=True)


async def save_upload(upload: UploadFile, directory: Path, settings: Settings) -> Path:
    """Сохраняет файл кусками и обрывает загрузку, как только превышен лимит."""
    # имя файла от клиента в путь не берём, только расширение
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in settings.allowed_extensions:
        suffix = ".bin"  # validate_audio отвергнет с понятным сообщением
    dest = directory / f"source{suffix}"

    max_bytes = settings.max_upload_mb * 1024 * 1024
    written = 0
    with dest.open("wb") as out:
        while chunk := await upload.read(_CHUNK):
            written += len(chunk)
            if written > max_bytes:
                raise FileTooLargeError(f"Файл больше {settings.max_upload_mb} МБ")
            out.write(chunk)
    return dest


def cleanup_expired(ttl_minutes: int) -> None:
    """Удаляет папки задач старше TTL."""
    root = Path(get_settings().upload_dir)
    if not root.exists():
        return
    cutoff = time.time() - ttl_minutes * 60
    for child in root.iterdir():
        if child.is_dir() and child.stat().st_mtime < cutoff:
            shutil.rmtree(child, ignore_errors=True)