from fastapi import FastAPI

app = FastAPI(
    title="LinguaVoice API",
    description="English-to-Slovak AI audio",
    version="0.1.0"
)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "linguavoice-api"}