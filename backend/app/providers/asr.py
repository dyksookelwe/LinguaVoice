from functools import lru_cache
from pathlib import Path
from typing import TypedDict

from app.config import get_settings


class WordTimestamp(TypedDict):
    text: str
    start: float
    end: float


@lru_cache(maxsize=2)
def _load_model(device: str, compute_type: str):
    # torch импортируем первым: он подтягивает библиотеки CUDA, которые нужны Whisper
    try:
        import torch  # noqa: F401
    except ImportError:
        pass
    from faster_whisper import WhisperModel

    return WhisperModel(get_settings().asr_model, device=device, compute_type=compute_type)


def _run(wav_path: Path, device: str, compute_type: str) -> list[WordTimestamp]:
    model = _load_model(device, compute_type)
    segments, _info = model.transcribe(
        str(wav_path), language=get_settings().asr_language, word_timestamps=True
    )
    words: list[WordTimestamp] = []
    for segment in segments:  # распознавание происходит во время этого цикла
        for word in segment.words or []:
            words.append(
                {"text": word.word.strip(), "start": float(word.start), "end": float(word.end)}
            )
    return words


def release_model() -> None:
    """Выгружает Whisper из памяти, чтобы освободить видеокарту для озвучки."""
    import gc

    _load_model.cache_clear()
    gc.collect()
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass


def transcribe_words(wav_path: Path) -> list[WordTimestamp]:
    """Return words with timestamps from the ASR model. No segmentation logic."""
    try:
        try:
            return _run(wav_path, "cuda", "float16")
        except Exception:
            # видеокарта недоступна или не хватило памяти: медленнее, но работает
            return _run(wav_path, "cpu", "int8")
    finally:
        release_model()