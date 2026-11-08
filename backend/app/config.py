import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# .env лежит в корне проекта (на два уровня выше папки app)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


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
    deepl_api_key: str = field(default=os.getenv("DEEPL_API_KEY", ""), repr=False)
    tts_chars_per_sec: float = float(os.getenv("TTS_CHARS_PER_SEC", "14"))
    length_tolerance: float = float(os.getenv("LENGTH_TOLERANCE", "1.1"))


def get_settings() -> Settings:
    return Settings()
