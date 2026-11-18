from functools import lru_cache

from app.config import get_settings


@lru_cache(maxsize=1)
def get_xtts():
    """Загружает XTTS один раз и переиспользует (загрузка занимает время)."""
    import torch
    from TTS.api import TTS

    device = "cuda" if torch.cuda.is_available() else "cpu"
    return TTS(get_settings().xtts_model).to(device)