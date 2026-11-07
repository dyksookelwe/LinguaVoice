import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "10"))
    max_duration_seconds: int = int(os.getenv("MAX_DURATION_SECONDS", "120"))
    upload_dir: str = os.getenv("UPLOAD_DIR", "var/uploads")
    sample_rate: int = int(os.getenv("SAMPLE_RATE", "16000"))
    allowed_extensions: tuple[str, ...] = (".mp3", ".wav")
    upload_ttl_minutes: int = int(os.getenv("UPLOAD_TTL_MINUTES", "1440"))


def get_settings() -> Settings:
    return Settings()
