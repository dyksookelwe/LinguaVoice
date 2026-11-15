import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.audio.validate import FileTooLargeError, InvalidAudioError, validate_audio
from app.config import get_settings
from app.schemas.job import Job, JobStatus, JobView, SegmentView
from app.services.jobs import get_job, run_job, save_job
from app.services.storage import (
    cleanup_expired,
    create_job_dir,
    remove_job_dir,
    save_upload,
)

router = APIRouter()

READY = {JobStatus.done, JobStatus.needs_review}


def _get_or_404(job_id: str) -> Job:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(404, "Задача не найдена")
    return job


@router.post("/jobs", status_code=status.HTTP_201_CREATED)
async def create_job(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
) -> dict:
    settings = get_settings()
    cleanup_expired(settings.upload_ttl_minutes)

    job_id = uuid.uuid4().hex
    directory = create_job_dir(job_id)
    try:
        source_path = await save_upload(file, directory, settings)
        audio = validate_audio(source_path)
    except InvalidAudioError as exc:
        remove_job_dir(job_id)
        code = 413 if isinstance(exc, FileTooLargeError) else 422
        raise HTTPException(code, str(exc)) from exc
    except Exception:
        remove_job_dir(job_id)
        raise

    job = save_job(Job(id=job_id, source_path=str(source_path)))
    background_tasks.add_task(run_job, job.id)
    return {
        "job_id": job.id,
        "status": job.status,
        "duration_seconds": round(audio.duration_seconds, 2),
    }


@router.get("/jobs/{job_id}", response_model=JobView)
def read_job(job_id: str) -> JobView:
    job = _get_or_404(job_id)
    return JobView(
        id=job.id,
        status=job.status,
        error=job.error,
        segments=[
            SegmentView(**segment.model_dump(exclude={"audio_path"}))
            for segment in job.segments
        ],
        metrics=job.metrics,
        audio_ready=job.status in READY and job.output_path is not None,
    )


@router.get("/jobs/{job_id}/audio")
def download_audio(job_id: str, format: str = "mp3") -> FileResponse:
    job = _get_or_404(job_id)
    if format not in ("mp3", "wav"):
        raise HTTPException(422, "Параметр format: mp3 или wav")
    if job.status not in READY:
        raise HTTPException(409, "Дубляж ещё не готов")
    raw = job.output_mp3_path if format == "mp3" else job.output_path
    if not raw or not Path(raw).exists():
        raise HTTPException(410, "Файл удалён по истечении срока хранения")
    media = "audio/mpeg" if format == "mp3" else "audio/wav"
    return FileResponse(raw, media_type=media, filename=f"dubbed-{job.id[:8]}.{format}")


@router.get("/jobs/{job_id}/original")
def download_original(job_id: str) -> FileResponse:
    job = _get_or_404(job_id)
    path = Path(job.source_path)
    if not path.exists():
        raise HTTPException(410, "Файл удалён по истечении срока хранения")
    media = "audio/mpeg" if path.suffix.lower() == ".mp3" else "audio/wav"
    return FileResponse(path, media_type=media)