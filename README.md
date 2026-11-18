# LinguaVoice

LinguaVoice is a local research demo that dubs short Slovak speech recordings into US English. It uses faster-whisper for transcription, DeepL for translation, XTTS-v2 for voice synthesis, and FFmpeg for audio conversion, alignment, and export.

The Slovak web interface accepts MP3 and WAV recordings. The default limits are 10 MB and 120 seconds. Use a clear recording with one speaker. The interface shows processing status, source and translated segments, timing metrics, and both audio players. The English dub is available as MP3 and WAV.

## Run locally on Windows

Use Python 3.11, FFmpeg with `ffmpeg` and `ffprobe` on PATH, and a DeepL API key. Internet access is needed for model downloads and DeepL requests. The recorded experiments used an NVIDIA RTX 2060 with 6 GB of VRAM. The code also supports CPU inference, which takes longer.

Open PowerShell in the repository root. Check the executables and create the virtual environment.

```powershell
py -3.11 --version
Get-Command ffmpeg,ffprobe
py -3.11 -m venv .venv-tts
```

Install PyTorch and torchaudio for the hardware you will use. The CUDA 12.4 setup below is the one used in the recorded experiments.

```powershell
.\.venv-tts\Scripts\python.exe -m pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
```

For a CPU-only installation, use the CPU wheel index instead.

```powershell
.\.venv-tts\Scripts\python.exe -m pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu
```

Install the application dependencies and create the local configuration if it is missing.

```powershell
.\.venv-tts\Scripts\python.exe -m pip install -r backend/requirements.txt coqui-tts==0.28.0
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Set `DEEPL_API_KEY` in the repository-root `.env`. Then start the server from the repository root.

```powershell
Set-Location backend
..\.venv-tts\Scripts\python.exe -m uvicorn app.main:app
```

Open [the web interface](http://127.0.0.1:8000) or [the interactive API documentation](http://127.0.0.1:8000/docs). FastAPI serves the HTML directly, so installation requires no frontend build. The first dubbing job can download the model weights and prompt for acceptance of the XTTS model terms in the terminal.

Use recordings from speakers who consented to voice cloning. LinguaVoice processes audio locally and sends transcribed text to DeepL for translation. Keep `.env`, recordings, and generated files out of Git.

## Verify the application

From `backend`, run the automated suite. The audio tests use FFmpeg and FFprobe. Tests substitute provider responses and require neither model downloads nor a DeepL key.

```powershell
..\.venv-tts\Scripts\python.exe -m pytest -q
```

For an end-to-end check with the real providers, upload a short Slovak recording in the browser. Wait for the dub, compare the transcript and translation, play both tracks, and open the downloaded MP3 and WAV. A result flagged for review still has playable audio. Verify that selecting a segment jumps to its original and dubbed timestamps. See [experiments](docs/experiments.md) for the recorded pipeline run and the scope of its measurements.

## Current scope

- The pipeline handles Slovak input and English output. The browser displays the transcript and translation for review. Editing, segment regeneration, video, and multi-speaker dubbing are outside the current demo.
- Timing can drift when the translation does not fit its source segment. The interface reports segment start delay and duration metrics.
- A single server process runs one dubbing job at a time. Restarting the server clears job status. Files can remain until cleanup is triggered by a later upload.
- The demo runs locally. The application has no authentication or per-user job isolation.

## Project documentation

- [Architecture, API, and settings](docs/architecture.md)
- [Implementation decisions and open research questions](docs/decisions.md)
- [Recorded experiments and verification procedure](docs/experiments.md)
- [Original proposal in Git history](https://github.com/dyksookelwe/LinguaVoice/blob/8e4c0b258772893c7a11613649176d83470b18c1/README.md)
