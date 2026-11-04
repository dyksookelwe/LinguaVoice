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
        translate_segment(en_text, src_duration) -> sk_text
        synthesize_segment(segment, reference_wav) -> segment wav
        align_segment(segment) -> stretch_ratio, gen_duration
  -> assemble_track(segments) -> output_path
  -> compute_metrics(job) -> Metrics
```

`Segment` is the unit of work: `id`, `start`, `end`, `en_text`, `sk_text`, `audio_path`, `src_duration`, `gen_duration`, `stretch_ratio`.

## Module boundaries

- `app/audio/` — file validation, conversion, alignment, export. Pure functions.
- `app/services/` — pipeline orchestration and per-step application logic.
- `app/providers/` — thin adapters to ASR / NMT / TTS / cloning. No job workflow here.
- `app/api/` — HTTP. Does not call models directly.
- `app/schemas/` — job, segment, and metrics shapes.

## Stage 0 status

Function signatures and the orchestrator exist. Step implementations raise `NotImplementedError` until their stage lands.
