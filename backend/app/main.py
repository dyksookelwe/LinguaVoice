from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.api.health import router as health_router
from app.api.jobs import router as jobs_router

FRONTEND_PAGE = Path(__file__).resolve().parents[2] / "frontend" / "index.html"

app = FastAPI(
    title="LinguaVoice API",
    description="SK to EN voice-preserving dubbing pipeline",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(jobs_router)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    if not FRONTEND_PAGE.exists():
        raise HTTPException(404, "Файл frontend/index.html не найден")
    return FileResponse(FRONTEND_PAGE)