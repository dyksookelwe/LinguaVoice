from functools import lru_cache

import deepl

from app.config import get_settings


@lru_cache(maxsize=1)
def _translator() -> deepl.DeepLClient:
    key = get_settings().deepl_api_key
    if not key:
        raise RuntimeError("DEEPL_API_KEY не задан: добавьте ключ в файл .env")
    return deepl.DeepLClient(key)


def translate_sk_to_en(src_text: str) -> str:
    """Перевод одного фрагмента через DeepL. Никакой логики пайплайна здесь нет."""
    if not src_text.strip():
        return ""
    result = _translator().translate_text(
        src_text, source_lang="SK", target_lang="EN-US"
    )
    return result.text


def get_usage() -> tuple[int, int]:
    """Сколько символов уже потрачено и какой лимит (count, limit)."""
    usage = _translator().get_usage()
    return usage.character.count, usage.character.limit