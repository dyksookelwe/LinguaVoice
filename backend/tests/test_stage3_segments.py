from app.providers.asr import WordTimestamp
from app.services.transcribe import build_segments


def w(text: str, start: float, end: float) -> WordTimestamp:
    return {"text": text, "start": start, "end": end}


def test_empty_input():
    assert build_segments([], 0.35, 1.0, 8.0) == []


def test_split_on_pause():
    words = [w("Ahoj", 0, 0.5), w("svet.", 0.55, 1.2),
             w("Dobrý", 2.2, 2.8), w("deň.", 2.85, 3.5)]
    segs = build_segments(words, 0.35, 1.0, 8.0)
    assert [s.src_text for s in segs] == ["Ahoj svet.", "Dobrý deň."]
    assert segs[0].start == 0 and segs[0].end == 1.2
    assert segs[1].duration == 1.3 - 0.0 or abs(segs[1].duration - 1.3) < 1e-6


def test_merge_short_piece():
    words = [w("Hej.", 0, 0.4), w("Ako", 1.4, 1.8),
             w("sa", 1.85, 2.0), w("máš?", 2.05, 2.6)]
    segs = build_segments(words, 0.35, 1.0, 8.0)
    assert len(segs) == 1
    assert segs[0].src_text == "Hej. Ako sa máš?"


def test_split_long_at_biggest_gap():
    words, t = [], 0.0
    for i in range(8):
        if i > 0:
            t += 0.5 if i == 4 else 0.1
        words.append(w(f"w{i}", t, t + 1.0))
        t += 1.0
    segs = build_segments(words, 5.0, 1.0, 6.0)
    assert len(segs) == 2
    assert segs[0].src_text == "w0 w1 w2 w3"
    assert segs[1].src_text == "w4 w5 w6 w7"


def test_segment_ids_are_sequential():
    words = [w("a", 0, 1.0), w("b", 3.0, 4.0), w("c", 6.0, 7.0)]
    segs = build_segments(words, 0.35, 0.5, 8.0)
    assert [s.id for s in segs] == ["seg-1", "seg-2", "seg-3"]