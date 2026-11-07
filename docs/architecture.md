# Architecture

LinguaVoice is a function pipeline, not a single AI prompt.

The API creates a job. `run_pipeline(job)` then calls application functions in a fixed order and passes structured data between them. Specialized models (ASR, NMT, TTS, voice cloning) are used only inside their own step.

## Data flow

```text
Job(source_path)
  -> validate_audio(path) -> ValidatedAudio
  -> convert_to_wav(audio) -> wav_path
  -> transcribe_and_segment(wav_path) -> list[Segment]
  -> for each Segment:
        translate_segment(src_text, src_duration) -> tgt_text
        synthesize_segment(segment, reference_wav) -> segment wav
        align_segment(segment) -> stretch_ratio, gen_duration
  -> assemble_track(segments) -> output_path
  -> compute_metrics(job) -> Metrics
```

`Segment` is the unit of work: `id`, `start`, `end`, `src_text`, `tgt_text`, `audio_path`, `src_duration`, `gen_duration`, `stretch_ratio`.

## Module boundaries

- `app/audio/` — file validation, conversion, alignment, export. Pure functions.
- `app/services/` — pipeline orchestration and per-step application logic.
- `app/providers/` — thin adapters to ASR / NMT / TTS / cloning. No job workflow here.
- `app/api/` — HTTP. Does not call models directly.
- `app/schemas/` — job, segment, and metrics shapes.

## Stage 1 status

Audio intake is implemented: `validate_audio` checks extension, size, real
content (via ffprobe) and duration; `convert_to_wav` produces mono 16 kHz WAV.
`POST /jobs` saves the upload to `var/uploads/<job_id>/`, validates it and
creates a Job. Invalid files are rejected (413 too large, 422 other) and their
folder is removed immediately; old folders are removed after
`UPLOAD_TTL_MINUTES`. Translation direction is fixed to SK -> EN.

Remaining steps still raise `NotImplementedError` until their stage lands.
## Stage 3 status

`transcribe_words` (providers/asr.py) runs faster-whisper `large-v3`
(GPU float16, CPU int8 fallback) and returns words with timestamps; the
language is set in config (`ASR_LANGUAGE`, default `sk`).
`transcribe_and_segment` (services/transcribe.py) builds segments with our own
rules: split on pauses (`SEGMENT_PAUSE_SEC`), merge short pieces
(`SEGMENT_MIN_SEC`), split long ones at the biggest pause (`SEGMENT_MAX_SEC`).
The rules are covered by `tests/test_stage3_segments.py` without loading the
model.