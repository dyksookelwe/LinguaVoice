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
