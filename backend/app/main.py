from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.jobs import router as jobs_router

app = FastAPI(
    title="LinguaVoice API",
    description="SK to EN voice-preserving dubbing pipeline",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(jobs_router)