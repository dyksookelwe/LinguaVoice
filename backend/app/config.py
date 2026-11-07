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
    segment_pause_sec: float = float(os.getenv("SEGMENT_PAUSE_SEC", "0.35"))
    segment_min_sec: float = float(os.getenv("SEGMENT_MIN_SEC", "1.5"))
    segment_max_sec: float = float(os.getenv("SEGMENT_MAX_SEC", "8.0"))
    asr_model: str = os.getenv("ASR_MODEL", "large-v3")
    asr_language: str = os.getenv("ASR_LANGUAGE", "sk")


def get_settings() -> Settings:
    return Settings()
