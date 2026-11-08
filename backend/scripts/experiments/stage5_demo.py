import sys
from pathlib import Path

# чтобы работал импорт пакета app при запуске скрипта из любой папки
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.audio.convert import convert_to_wav  # noqa: E402
from app.audio.validate import validate_audio  # noqa: E402
from app.services.synthesize import synthesize_segment  # noqa: E402
from app.services.transcribe import transcribe_and_segment  # noqa: E402
from app.services.translate import is_text_too_long, translate_segment  # noqa: E402

SAMPLES = Path(__file__).resolve().parents[1] / "samples_raw"
SOURCE = SAMPLES / "sk_long.mp3"

wav = convert_to_wav(validate_audio(SOURCE))
segments = transcribe_and_segment(wav)
print(f"сегментов: {len(segments)}\n")

rates = []
for seg in segments:
    seg.src_duration = seg.duration
    seg.tgt_text = translate_segment(seg.src_text, seg.src_duration)
    seg.text_too_long = is_text_too_long(seg.tgt_text, seg.src_duration)
    out = synthesize_segment(seg, wav, use_cloning=True)
    rate = len(seg.tgt_text) / seg.gen_duration
    rates.append(rate)
    print(
        f"{seg.id}: voice={seg.voice} src={seg.src_duration:.1f}s "
        f"gen={seg.gen_duration:.1f}s ratio={seg.gen_duration / seg.src_duration:.2f} "
        f"chars/s={rate:.1f} too_long_flag={seg.text_too_long}"
    )
    print(f"    {seg.tgt_text}")
    print(f"    -> {out}")

print(f"\nсреднее chars/s по озвучке: {sum(rates) / len(rates):.1f}")