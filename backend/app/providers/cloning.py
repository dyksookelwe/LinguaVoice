from pathlib import Path


def clone_speech(text: str, reference_wav: Path, language: str = "sk") -> Path:
    """Synthesize speech that follows the reference voice."""
    raise NotImplementedError("Voice cloning adapter is implemented in stage 5")
