import time
from pathlib import Path

import torch
from TTS.api import TTS

HERE = Path(__file__).resolve().parent
SAMPLES = HERE.parent / "samples_raw"
REFERENCE = SAMPLES / "sk_sample.wav"

TEXT = (
    "Today we are testing how well the system keeps the speaker's voice "
    "when the language changes. The goal is natural speech with the same timing."
)

device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

t0 = time.perf_counter()
tts.tts_to_file(
    text=TEXT,
    speaker_wav=str(REFERENCE),
    language="en",
    file_path=str(SAMPLES / "out_xtts_en_long_clone.wav"),
)
print(f"clone, long phrase: {time.perf_counter() - t0:.1f} s")

t0 = time.perf_counter()
tts.tts_to_file(
    text=TEXT,
    speaker="Claribel Dervla",
    language="en",
    file_path=str(SAMPLES / "out_xtts_en_long_fallback.wav"),
)
print(f"fallback (built-in voice): {time.perf_counter() - t0:.1f} s")