from pathlib import Path

from app.config import get_settings
from app.providers.asr import WordTimestamp, transcribe_words
from app.schemas.segment import Segment


def _span(group: list[WordTimestamp]) -> float:
    return group[-1]["end"] - group[0]["start"]


def _split_on_pauses(words: list[WordTimestamp], pause_sec: float) -> list[list[WordTimestamp]]:
    groups: list[list[WordTimestamp]] = [[words[0]]]
    for prev, word in zip(words, words[1:]):
        if word["start"] - prev["end"] >= pause_sec:
            groups.append([])
        groups[-1].append(word)
    return groups


def _merge_short(
    groups: list[list[WordTimestamp]], min_sec: float, max_sec: float
) -> list[list[WordTimestamp]]:
    result: list[list[WordTimestamp]] = []
    for group in groups:
        if (
            result
            and (_span(result[-1]) < min_sec or _span(group) < min_sec)
            and _span(result[-1] + group) <= max_sec
        ):
            result[-1] = result[-1] + group
        else:
            result.append(group)
    return result


def _split_long(group: list[WordTimestamp], max_sec: float) -> list[list[WordTimestamp]]:
    if len(group) < 2 or _span(group) <= max_sec:
        return [group]
    gaps = [group[i + 1]["start"] - group[i]["end"] for i in range(len(group) - 1)]
    cut = gaps.index(max(gaps)) + 1
    return _split_long(group[:cut], max_sec) + _split_long(group[cut:], max_sec)


def build_segments(
    words: list[WordTimestamp], pause_sec: float, min_sec: float, max_sec: float
) -> list[Segment]:
    """Наши правила: резать по паузам, клеить короткие, делить длинные."""
    words = [w for w in words if w["text"].strip()]
    if not words:
        return []
    groups = _split_on_pauses(words, pause_sec)
    groups = _merge_short(groups, min_sec, max_sec)
    groups = [part for g in groups for part in _split_long(g, max_sec)]
    return [
        Segment(
            id=f"seg-{i}",
            start=round(g[0]["start"], 3),
            end=round(g[-1]["end"], 3),
            src_text=" ".join(w["text"].strip() for w in g),
        )
        for i, g in enumerate(groups, start=1)
    ]


def transcribe_and_segment(wav_path: Path) -> list[Segment]:
    """Turn ASR timestamps into segments using pause and length rules."""
    settings = get_settings()
    words = transcribe_words(wav_path)
    return build_segments(
        words,
        settings.segment_pause_sec,
        settings.segment_min_sec,
        settings.segment_max_sec,
    )