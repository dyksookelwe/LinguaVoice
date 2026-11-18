import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.providers.cloning import clone_speech  # noqa: E402

S = Path(__file__).resolve().parents[1] / "samples_raw"
TEXT = (
    "Did you know that butterflies taste with their feet? "
    "When a butterfly lands on a flower, its legs help it find food."
)

for name in ("ref_24k", "ref_denoised_soft"):
    out = clone_speech(TEXT, S / f"{name}.wav", S / f"out_{name}.wav")
    print(out)