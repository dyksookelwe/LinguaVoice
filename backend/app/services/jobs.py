from app.schemas.job import Job

_jobs: dict[str, Job] = {}


def save_job(job: Job) -> Job:
    _jobs[job.id] = job
    return job


def get_job(job_id: str) -> Job | None:
    return _jobs.get(job_id)
