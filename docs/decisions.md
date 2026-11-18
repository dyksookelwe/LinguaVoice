# Implementation decisions

## D-001 — Scope and language direction

The demo accepts short single-speaker Slovak recordings and produces US English audio. The original proposal described English-to-Slovak dubbing. The implemented direction follows the Slovak-source and English-output experiments. The browser supports review and playback. Text editing, segment regeneration, broader language support, and public deployment remain outside the current implementation.

## D-002 — Voice synthesis

XTTS-v2 runs locally and uses the uploaded recording as the voice reference. The same model supplies a built-in English speaker as the fallback. Keeping both paths in one runtime avoids a second service and an additional API dependency. The fallback shares the XTTS model, so a model load failure can affect both paths.

Earlier listening trials explored ElevenLabs Instant, Cartesia, and Polyvox. Those trials were informal. Cloud voice cloning adapters are outside the current implementation. See [experiments](experiments.md) for the XTTS measurements and their limits.

## D-003 — Runtime and speech recognition

The documented Windows setup uses a single Python 3.11 environment for FastAPI, faster-whisper, and XTTS. The recorded GPU runs used PyTorch 2.6.0 with CUDA 12.4. The ASR adapter defaults to `large-v3` based on the observed transcription quality on the Slovak test sample. Formal word error rate was not measured. Whisper releases its model after transcription to free accelerator memory before synthesis.

## D-004 — Translation and segmentation

The application owns segmentation and calls the DeepL adapter for Slovak-to-English translation. DeepL is the only implemented translation provider. The app sends transcript segments to DeepL while keeping audio processing local. API credentials are configured outside Git.

A rate of 16 characters per second approximates speech length. This estimate flags translations for review. It does not shorten the text or force the synthesizer to match a segment duration.

## D-005 — Alignment and evaluation

The aligner uses a limited tempo adjustment to preserve speech quality. Segments outside the supported ratio keep their generated tempo, so a long segment can shift later segments. Timing metrics and the cloned-segment share are available in the UI. Voice similarity and intelligibility still need evaluation with more speakers and blinded listeners. A speaker-similarity model could complement listening tests if its cross-language behavior is documented.

## D-006 — Job execution

FastAPI background tasks and an in-process lock allow one dubbing job to run at a time. This keeps the local demo runnable with one server process and no external queue or database. Job status is lost on restart. Audio is stored on disk and cleaned up during later uploads. The current API has no user authentication or job ownership checks. See [architecture](architecture.md) for the lifecycle and storage details.
