from pathlib import Path

from app.providers.xtts import get_xtts


def clone_speech(
    text: str, reference_wav: Path, output_path: Path, language: str = "en"
) -> Path:
    """Synthesize speech that follows the reference voice."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    get_xtts().tts_to_file(
        text=text,
        speaker_wav=str(reference_wav),
        language=language,
        file_path=str(output_path),
    )
    return output_path