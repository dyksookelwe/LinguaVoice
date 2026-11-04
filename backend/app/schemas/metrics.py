from pydantic import BaseModel


class Metrics(BaseModel):
    pipeline_seconds: float = 0.0
    source_duration: float = 0.0
    dubbed_duration: float = 0.0
    duration_ratio: float = 1.0
    overstretched_segment_ratio: float = 0.0
