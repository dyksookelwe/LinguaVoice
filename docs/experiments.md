# Experiments and verification

The recorded experiments used an NVIDIA GeForce RTX 2060 with 6 GB of VRAM and Python 3.11. Torch was version 2.6.0 with CUDA 12.4, and coqui-tts was version 0.28.0. Timings describe individual runs and depend on the clip, device, cache state, and model output.

## Voice cloning with XTTS-v2

The reference was 13 seconds of Slovak speech from one speaker, recorded as a mono 24 kHz WAV. The target phrases were English. The experiment scripts are [clone_xtts.py](../backend/scripts/experiments/clone_xtts.py) and [fallback_xtts.py](../backend/scripts/experiments/fallback_xtts.py).

| Case | Time |
|---|---:|
| First model load, including about 2 GB of downloads | 99.5 s |
| Clone, short phrase | 5.7 s |
| Clone, two-sentence phrase | 8.0 s |
| Built-in voice, same two-sentence phrase | 5.8 s |

One listener described the clone as similar in timbre and intelligible, with a slightly robotic quality on the longer phrase. The built-in voice sounded like a different speaker and was judged unnatural. Speaker similarity was assessed by listening to a single reference sample.

## Slovak speech recognition

The comparison used one approximately 26-second Slovak sample with CUDA float16. The [ASR experiment script](../backend/scripts/experiments/asr_whisper.py) reports model loading and transcription separately.

| Model | Transcription time | Listening and transcript review |
|---|---:|---|
| `small` | Unrecorded | Many errors, with the beginning missing |
| `medium` | 2.9 s | Several word errors |
| `large-v3` | 4.1 s | Minor diacritic errors, with the meaning preserved |

Timestamps followed the speaker's pauses in this sample. The comparison was qualitative, and no formal word error rate was calculated. Recognition errors can propagate into translation. The current interface displays the transcript for review.

## Segment synthesis

The six segments below come from the [stage 5 experiment](../backend/scripts/experiments/stage5_demo.py). Durations and ratios are rounded. This experiment measured synthesis before alignment.

| Segment | Source window | Generated speech | Duration ratio | Characters/s |
|---|---:|---:|---:|---:|
| seg-1 | 2.5 s | 2.8 s | 1.12 | 18.7 |
| seg-2 | 6.0 s | 6.3 s | 1.05 | 16.1 |
| seg-3 | 3.6 s | 4.4 s | 1.20 | 16.7 |
| seg-4 | 4.3 s | 4.8 s | 1.11 | 16.1 |
| seg-5 | 2.5 s | 2.7 s | 1.08 | 15.2 |
| seg-6 | 4.9 s | 6.1 s | 1.25 | 14.6 |

The mean generation rate was 16.2 characters per second. Four of the six segments exceeded the 1.1 ratio later adopted as the upper alignment limit. A separate listening comparison found the 24 kHz voice reference slightly cleaner than the 16 kHz reference. The current pipeline generates the 24 kHz voice reference separately from the 16 kHz ASR input.

## Recorded pipeline run

The [stage 6 script](../backend/scripts/experiments/stage6_demo.py) ran the real processing pipeline directly on an approximately 26-second Slovak recording. It called transcription, translation, synthesis, alignment, and export in one run. This experiment exercised the pipeline through Python. The browser workflow has its own check below.

| Metric | Recorded value |
|---|---:|
| Pipeline time, including Whisper and XTTS loading | 99.31 s |
| Source segment span | 25.46 s |
| Sum of dubbed segment durations | 29.91 s |
| Duration ratio | 1.175 |
| Segments outside the 0.9–1.1 pre-alignment range | 5 of 6 (83%) |
| Maximum segment start delay | 2.92 s |
| Segments voiced by the clone | 6 of 6 |

The English segments occupied more time than the source window, so later segments started after their original timestamps. See [metric definitions](architecture.md#metrics) for how the segment metrics relate to file durations. Timing and similarity require more speakers and repeated runs before drawing broader conclusions.

## Repeat the pipeline and check the browser

For the pipeline-only run, place a consented Slovak recording at `backend/scripts/samples_raw/sk_long.mp3`. With the [local setup](../README.md#run-locally-on-windows) complete, run this from the repository root.

```powershell
.\.venv-tts\Scripts\python.exe backend/scripts/experiments/stage6_demo.py
```

The script copies the input to `backend/var/demo/` and writes `dubbed.wav`, `dubbed.mp3`, and `metrics.json` there. Sample recordings and outputs are ignored by Git.

For the browser check, start the server, upload a consented Slovak recording from the UI, and wait for completion. Compare the Slovak transcript and English translation, listen to both tracks, select a segment to check the playback timestamps, and open both downloaded formats. Record the input duration, pipeline time, review status, and observed timing and speech-quality issues. This check uses actual model inference and the live DeepL API.
