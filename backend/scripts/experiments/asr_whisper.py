import time
from pathlib import Path

import torch  # импортируем первым: подтягивает библиотеки CUDA
from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
SAMPLES = HERE.parent / "samples_raw"
AUDIO = SAMPLES / "sk_long.mp3"
if not AUDIO.exists():
    AUDIO = SAMPLES / "sk_sample.wav"

import sys
MODEL_NAME = sys.argv[1] if len(sys.argv) > 1 else "small"


def run(device: str, compute_type: str):
    t0 = time.perf_counter()
    model = WhisperModel(MODEL_NAME, device=device, compute_type=compute_type)
    print(f"model loaded in {time.perf_counter() - t0:.1f} s ({device})")

    t0 = time.perf_counter()
    segments, info = model.transcribe(str(AUDIO), language="sk", word_timestamps=True)
    segments = list(segments)  # реальная работа происходит здесь
    print(f"transcribed in {time.perf_counter() - t0:.1f} s, "
          f"audio length {info.duration:.1f} s")
    return segments


print("file:", AUDIO.name)
try:
    result = run("cuda", "float16")
except Exception as exc:
    print("GPU не сработала, переходим на процессор:", exc)
    result = run("cpu", "int8")

for s in result:
    print(f"[{s.start:6.2f} - {s.end:6.2f}] ({len(s.words)} слов) {s.text.strip()}")