from pathlib import Path


def synthesize_speech(text: str, language: str = "sk") -> Path:
    """Standard Slovak TTS fallback. Same output type as cloning."""
    raise NotImplementedError("TTS adapter is implemented in stage 5")
