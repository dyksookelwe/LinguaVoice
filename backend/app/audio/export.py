import shutil
import subprocess
import wave
from pathlib import Path

from app.schemas.segment import Segment


def _read_wav(path: Path) -> tuple[wave._wave_params, bytes]:
    with wave.open(str(path), "rb") as w:
        return w.getparams(), w.readframes(w.getnframes())


def assemble_track(segments: list[Segment], reference_wav: Path) -> Path:
    """Join aligned segments using original pause boundaries."""
    ordered = sorted((s for s in segments if s.audio_path), key=lambda s: s.start)
    if not ordered:
        raise ValueError("Нет озвученных сегментов для сборки дорожки")

    out_path = reference_wav.parent / "dubbed.wav"
    rate: int | None = None
    written = 0  # сколько отсчётов уже записано в дорожку

    with wave.open(str(out_path), "wb") as out:
        for seg in ordered:
            params, data = _read_wav(Path(seg.audio_path))
            if params.nchannels != 1 or params.sampwidth != 2:
                raise ValueError(f"{seg.id}: нужен моно 16-bit WAV")
            if rate is None:
                rate = params.framerate
                out.setnchannels(1)
                out.setsampwidth(2)
                out.setframerate(rate)
            elif params.framerate != rate:
                raise ValueError(f"{seg.id}: частота {params.framerate} Гц, ожидалась {rate} Гц")

            target = int(round(seg.start * rate))
            if target > written:  # есть место: вставляем паузу из оригинала
                out.writeframes(b"\x00\x00" * (target - written))
                written = target
            # если target < written, предыдущий сегмент не уложился: сдвигаем этот вправо
            seg.placed_start = written / rate
            out.writeframes(data)
            written += len(data) // 2

    return out_path


def export_mp3(wav_path: Path) -> Path:
    """Export the dubbed track as MP3 next to the WAV."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg не найден: установите его и добавьте в PATH")
    dst = wav_path.with_suffix(".mp3")
    result = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(wav_path),
         "-codec:a", "libmp3lame", "-q:a", "2", str(dst)],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg не смог создать MP3: {result.stderr[-300:]}")
    return dst