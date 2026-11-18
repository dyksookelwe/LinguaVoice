# Architecture

FastAPI serves the Slovak interface from [frontend/index.html](../frontend/index.html) and exposes the job API on the same origin. The browser sends a multipart upload, polls the job, and plays or downloads audio from the job endpoints. The application uses a single Python process and a local upload directory.

## Processing a job

1. The API saves the upload in chunks and validates its size, extension, content, and duration using FFprobe. An invalid upload's directory is removed before the API returns an error.
2. The API creates a job and schedules background processing. The worker takes a process-local lock, then revalidates the file and uses FFmpeg to create two mono PCM WAV files. At the defaults, `reference.wav` is 16 kHz for ASR and `voice_reference.wav` is 24 kHz for cloning.
3. Faster-whisper produces Slovak word timestamps. The adapter tries CUDA with float16, then retries on CPU with int8 if the GPU path fails. It releases the Whisper model after transcription. Segmentation splits at pauses, joins short neighboring groups when they fit the configured maximum, and recursively splits long groups at the largest word gap.
4. DeepL translates each segment from `SK` to `EN-US`. The application normalizes whitespace and punctuation and flags translations whose estimated speech duration exceeds the source segment duration multiplied by `LENGTH_TOLERANCE`.
5. XTTS-v2 synthesizes English from the source voice reference. If cloning is disabled, the reference is unavailable, or the cloning call fails, the application uses the model's built-in English voice. The XTTS model is cached in the server process.
6. The aligner records the generated-to-source duration ratio before tempo changes. It uses FFmpeg `atempo` for ratios within 0.9–1.1 when the deviation from 1 is at least 0.02. Out-of-range audio retains its generated tempo. The assembler inserts silence up to each original start time when space allows. If a preceding clip runs past the next start, the next clip is shifted.
7. The pipeline saves `dubbed.wav`, `dubbed.mp3`, and `metrics.json` in the job directory. The API reports metrics alongside source and translated text, source timestamps, and dubbed start times.

## HTTP API

| Request | Result |
|---|---|
| `GET /` | Slovak upload and comparison page |
| `GET /health` | Server status, with no dependency checks |
| `GET /docs` | Interactive OpenAPI documentation |
| `POST /jobs` | Accepts multipart field `file` and returns HTTP 201 with `job_id`, initial `status`, and measured upload `duration_seconds` |
| `GET /jobs/{job_id}` | Job status, error if present, segments, metrics, and `audio_ready` |
| `GET /jobs/{job_id}/original` | Original audio |
| `GET /jobs/{job_id}/audio?format=mp3` | Dubbed audio. `mp3` is the default and `wav` is also accepted. |

Jobs progress from `queued` to `processing` and finish as `done`, `needs_review`, or `failed`. A result is flagged for review when a segment has `text_too_long` set or a measured pre-alignment ratio outside 0.9–1.1. Both `done` and `needs_review` support playback and download.

Oversized uploads return 413. Unsupported or invalid audio and invalid export formats return 422. Unknown jobs return 404, unfinished dubs return 409, and known jobs whose requested files are missing return 410.

## Metrics

| Field | Calculation |
|---|---|
| `pipeline_seconds` | Elapsed time from pipeline entry through MP3 export, excluding queue wait and the metrics file write |
| `source_duration` | Last recognized segment end minus first recognized segment start |
| `dubbed_duration` | Sum of segment audio durations after alignment, excluding inserted silence |
| `duration_ratio` | `dubbed_duration / source_duration`, or zero when the source span is zero |
| `overstretched_segment_ratio` | Fraction of segments with a pre-alignment duration ratio outside 0.9–1.1 |
| `max_delay_seconds` | Largest positive difference between a dubbed segment's placed start and its original start |
| `clone_segment_ratio` | Fraction of segments synthesized with the reference voice |

The duration metrics describe segment timing. The upload duration comes from FFprobe, and the exported track may contain additional silence.

## Storage and configuration

The server reads `.env` from the repository root at startup. Relative upload paths are resolved from the server's working directory. With the README launch command, jobs use `backend/var/uploads/<job_id>/`. Job records live in memory. On each new upload, cleanup checks directory modification times and removes directories older than the configured TTL. A restart clears the job records, and file cleanup still depends on a subsequent upload. Run a single server worker so job status and the pipeline lock are shared within the process.

| Variable | Default | Purpose |
|---|---|---|
| `DEEPL_API_KEY` | Empty | Required for live translation |
| `MAX_UPLOAD_MB` / `MAX_DURATION_SECONDS` | `10` / `120` | Audio validation limits. The browser displays the default limits in its help text. |
| `UPLOAD_DIR` / `UPLOAD_TTL_MINUTES` | `var/uploads` / `1440` | Job storage and cleanup threshold |
| `SAMPLE_RATE` / `VOICE_SAMPLE_RATE` | `16000` / `24000` | ASR and voice-reference sample rates in Hz |
| `ASR_MODEL` / `ASR_LANGUAGE` | `large-v3` / `sk` | Whisper model and recognition language. The translation adapter uses Slovak as its source regardless. |
| `SEGMENT_PAUSE_SEC` / `SEGMENT_MIN_SEC` / `SEGMENT_MAX_SEC` | `0.35` / `1.5` / `8.0` | Segmentation pause threshold and target length bounds |
| `TTS_CHARS_PER_SEC` / `LENGTH_TOLERANCE` | `16` / `1.1` | Length-estimation heuristic |
| `XTTS_MODEL` | `tts_models/multilingual/multi-dataset/xtts_v2` | Model used for cloning and built-in speech |
| `XTTS_SPEAKER` / `CLONING_ENABLED` | `Claribel Dervla` / `true` | Built-in fallback speaker and voice cloning toggle |

## Code map

- [API](../backend/app/api) handles uploads, job status, downloads, and the health endpoint.
- [Services](../backend/app/services) implement the pipeline, job orchestration, segmentation, and metrics.
- [Providers](../backend/app/providers) adapt Whisper, DeepL, and XTTS.
- [Audio](../backend/app/audio) contains validation, conversion, alignment, and export.
- [Schemas](../backend/app/schemas) define the job, segment, and metric fields returned by the API.
