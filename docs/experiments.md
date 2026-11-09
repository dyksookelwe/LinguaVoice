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
## ASR: faster-whisper, Slovak speech (26 s sample, RTX 2060, float16)

| Model | Transcription time | Quality (subjective) |
|---|---|---|
| small | n/a (not recorded) | Many errors, start of the text lost |
| medium | 2.9 s | Several word errors ("motele", "krydla") |
| large-v3 | 4.1 s | Minor diacritics errors ("motyle", "oče"), meaning preserved |

Segment timestamps matched the speaker's pauses for all models. Language is
passed explicitly (`sk`). Whisper errors will propagate into translation, so
segment text must be editable before translation (Stage 8).
## Synthesis inside the pipeline: XTTS-v2 clone (26 s Slovak reference, 6 segments)

| Segment | Source, s | Generated, s | Ratio | chars/s |
|---|---|---|---|---|
| seg-1 | 2.5 | 2.8 | 1.12 | 18.7 |
| seg-2 | 6.0 | 6.3 | 1.05 | 16.1 |
| seg-3 | 3.6 | 4.4 | 1.20 | 16.7 |
| seg-4 | 4.3 | 4.8 | 1.11 | 16.1 |
| seg-5 | 2.5 | 2.7 | 1.08 | 15.2 |
| seg-6 | 4.9 | 6.1 | 1.25 | 14.6 |

Mean speech rate: 16.2 chars/s (`TTS_CHARS_PER_SEC` set to 16). English audio is
5-25 % longer than the Slovak source; 4 of 6 segments exceed the 1.1 stretch
limit planned for Stage 6.

Reference sample rate: a 24 kHz reference gave a slightly cleaner clone than
16 kHz (subjective, one listener), so cloning uses a separate 24 kHz reference
while ASR keeps 16 kHz. Remaining artifacts: a slight robotic noise in clone
output; fallback (built-in voice) sounds clearly robotic. Whisper is unloaded
from GPU memory before synthesis (6 GB card).
## Full pipeline run (26 s Slovak recording, 6 segments, RTX 2060)

| Metric | Value |
|---|---|
| Pipeline time | 99 s (includes loading Whisper and XTTS) |
| Source duration | 25.5 s |
| Dubbed duration | 29.9 s |
| Duration ratio | 1.17 |
| Segments outside the 0.9-1.1 stretch limit | 5 of 6 (83 %) |
| Max delay of a segment vs. original | 2.9 s |
| Segments voiced by the clone | 6 of 6 |

English speech is longer than Slovak, and the original has short pauses, so the
delay accumulates towards the end of the track. This is measured by our own
formula (`compute_metrics`), as planned: naturalness has priority over speed
adjustment. XTTS output varies between runs