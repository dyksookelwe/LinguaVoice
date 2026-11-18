import pytest

from app.services.translate import (
    estimate_speech_seconds,
    is_text_too_long,
    normalize_text,
    translate_segment,
)


def test_normalize_text():
    assert normalize_text("  Hello   world , ok ! ") == "Hello world, ok!"


def test_estimate_speech_seconds():
    assert estimate_speech_seconds("a" * 32) == pytest.approx(2.0)


def test_text_too_long_when_exceeds_window():
    assert is_text_too_long("a" * 28, 1.0) is True


def test_text_fits_when_within_tolerance():
    assert is_text_too_long("a" * 28, 2.0) is False


def test_empty_text_or_zero_duration_not_flagged():
    assert is_text_too_long("", 2.0) is False
    assert is_text_too_long("abc", 0.0) is False


def test_translate_segment_normalizes_input_and_output(monkeypatch):
    seen = []

    def fake_engine(text):
        seen.append(text)
        return "  Did you know ,  ok "

    monkeypatch.setattr("app.services.translate.translate_sk_to_en", fake_engine)
    assert translate_segment("  Vedeli   ste ?  ", 3.0) == "Did you know, ok"
    assert seen == ["Vedeli ste?"]