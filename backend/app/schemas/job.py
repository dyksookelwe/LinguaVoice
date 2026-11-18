from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.metrics import Metrics
from app.schemas.segment import Segment


class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    needs_review = "needs_review"
    done = "done"
    failed = "failed"


class Job(BaseModel):
    id: str
    source_path: str
    status: JobStatus = JobStatus.queued
    reference_wav_path: str | None = None
    output_path: str | None = None
    output_mp3_path: str | None = None
    segments: list[Segment] = Field(default_factory=list)
    metrics: Metrics | None = None
    error: str | None = None


class SegmentView(BaseModel):
    """Сегмент для клиента: без путей к файлам на сервере."""

    id: str
    start: float
    end: float
    src_text: str
    tgt_text: str
    src_duration: float
    gen_duration: float
    stretch_ratio: float
    text_too_long: bool
    voice: str
    placed_start: float

class JobView(BaseModel):
    id: str
    status: JobStatus
    error: str | None = None
    segments: list[SegmentView] = Field(default_factory=list)
    metrics: Metrics | None = None
    audio_ready: bool = False
