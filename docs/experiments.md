# Experiments

## Voice cloning: XTTS-v2 (local, coqui-tts 0.28.0)

**Setup.** Reference: 13 s Slovak speech sample (mono, 24 kHz, one speaker).
Target: English phrases. Hardware: NVIDIA GeForce RTX 2060 (6 GB), PyTorch
2.6.0+cu124, Python 3.11 (separate environment). Scripts:
`backend/scripts/experiments/clone_xtts.py` and `fallback_xtts.py`.

**Results.**

| Case | Time |
|---|---|
| Model load (first run, includes ~2 GB download) | 99.5 s |
| Clone, short phrase | 5.7 s |
| Clone, longer phrase (2 sentences) | 8.0 s |
| Built-in voice (fallback), longer phrase | 5.8 s |

**Listening notes (subjective, one listener).**
- Clone: timbre is similar to the original, not identical. Slightly robotic
  on the longer phrase. English is intelligible; no background noise.
- Built-in voice: different speaker by design; sounds unnatural.

**Limitations.**
- A Slovak reference is used for English output (cross-lingual cloning), which
  may lower similarity compared with an English reference of the same speaker.
- Only one reference sample and one listener, so no objective similarity score.
- Generation is a few seconds per phrase on GPU; first load is slow.