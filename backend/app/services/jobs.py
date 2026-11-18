import logging
import threading

from app.audio.align import MAX_STRETCH_RATIO, MIN_STRETCH_RATIO
from app.schemas.job import Job, JobStatus
from app.services.pipeline import run_pipeline

logger = logging.getLogger(__name__)

_jobs: dict[str, Job] = {}
# Одна видеокарта: пайплайн запускаем строго по одной задаче
_pipeline_lock = threading.Lock()


def save_job(job: Job) -> Job:
    _jobs[job.id] = job
    return job


def get_job(job_id: str) -> Job | None:
    return _jobs.get(job_id)


def needs_review(job: Job) -> bool:
    """Нашe правило: человеку стоит просмотреть результат."""
    return any(
        segment.text_too_long
        or not (MIN_STRETCH_RATIO <= segment.stretch_ratio <= MAX_STRETCH_RATIO)
        for segment in job.segments
    )


def run_job(job_id: str) -> None:
    """Фоновая обработка задачи: ждёт своей очереди, затем гонит пайплайн."""
    job = get_job(job_id)
    if job is None:
        return
    with _pipeline_lock:
        try:
            run_pipeline(job)
        except Exception as exc:
            logger.exception("Задача %s завершилась ошибкой", job_id)
            if job.status != JobStatus.failed:
                job.status = JobStatus.failed
                job.error = str(exc)
            return
    if needs_review(job):
        job.status = JobStatus.needs_review
