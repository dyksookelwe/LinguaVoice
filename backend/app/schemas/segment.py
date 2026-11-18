from pydantic import BaseModel


class Segment(BaseModel):
    id: str
    start: float
    end: float
    src_text: str = ""
    tgt_text: str = ""
    audio_path: str | None = None
    src_duration: float = 0.0
    gen_duration: float = 0.0
    stretch_ratio: float = 1.0
    text_too_long: bool = False
    voice: str = ""
    placed_start: float = 0.0

    @property
    def duration(self) -> float:
        return self.end - self.start
