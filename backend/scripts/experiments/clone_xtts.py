import time
from pathlib import Path

import torch
from TTS.api import TTS

HERE = Path(__file__).resolve().parent
SAMPLES = HERE.parent / "samples_raw"
REFERENCE = SAMPLES / "sk_sample.wav"
OUTPUT = SAMPLES / "out_xtts_en.wav"

TEXT = "Hello, this is a short test of my cloned voice speaking English."

device = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", device)

t0 = time.perf_counter()
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
print(f"model loaded in {time.perf_counter() - t0:.1f} s")

t0 = time.perf_counter()
tts.tts_to_file(
    text=TEXT,
    speaker_wav=str(REFERENCE),
    language="en",
    file_path=str(OUTPUT),
)
print(f"generated in {time.perf_counter() - t0:.1f} s -> {OUTPUT}")