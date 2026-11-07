import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.audio.validate import FileTooLargeError, InvalidAudioError, validate_audio
from app.config import get_settings
from app.schemas.job import Job
from app.services.jobs import save_job
from app.services.storage import (
    cleanup_expired,
    create_job_dir,
    remove_job_dir,
    save_upload,
)

router = APIRouter()


@router.post("/jobs", status_code=status.HTTP_201_CREATED)
async def create_job(file: UploadFile = File(...)) -> dict:
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
    return {
        "job_id": job.id,
        "status": job.status,
        "duration_seconds": round(audio.duration_seconds, 2),
    }