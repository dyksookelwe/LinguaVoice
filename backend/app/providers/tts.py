from pathlib import Path

from app.config import get_settings
from app.providers.xtts import get_xtts


def synthesize_speech(text: str, output_path: Path, language: str = "en") -> Path:
    """Standard TTS fallback (built-in voice). Same output type as cloning."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    get_xtts().tts_to_file(
        text=text,
        speaker=get_settings().xtts_speaker,
        language=language,
        file_path=str(output_path),
    )
    return output_path