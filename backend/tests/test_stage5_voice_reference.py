import wave
from pathlib import Path

from app.audio.convert import convert_to_wav, make_voice_reference
from app.audio.validate import validate_audio


def test_asr_wav_is_16k_and_voice_reference_is_24k(tmp_path: Path):
    src = tmp_path / "a.wav"
    with wave.open(str(src), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(b"\x00\x00" * 2 * 44100)

    audio = validate_audio(src)
    assert validate_audio(convert_to_wav(audio)).sample_rate == 16000
    ref = validate_audio(make_voice_reference(audio))
    assert ref.sample_rate == 24000
    assert ref.channels == 1