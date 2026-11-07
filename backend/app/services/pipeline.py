import time
from pathlib import Path

from app.audio.align import align_segment
from app.audio.convert import convert_to_wav
from app.audio.export import assemble_track
from app.audio.validate import validate_audio
from app.schemas.job import Job, JobStatus
from app.services.metrics import compute_metrics
from app.services.synthesize import synthesize_segment
from app.services.transcribe import transcribe_and_segment
from app.services.translate import translate_segment


def run_pipeline(job: Job) -> Job:
    """Run the dubbing steps in order. Each step is a named function."""
    started = time.perf_counter()
    job.status = JobStatus.processing
    try:
        validated = validate_audio(Path(job.source_path))
        wav_path = convert_to_wav(validated)
        job.reference_wav_path = str(wav_path)

        segments = transcribe_and_segment(wav_path)
        for segment in segments:
            segment.src_duration = segment.duration
            segment.tgt_text = translate_segment(
                segment.src_text, segment.src_duration
            )
            segment.audio_path = str(
                synthesize_segment(segment, wav_path, use_cloning=True)
            )
            align_segment(segment)

        job.segments = segments
        job.output_path = str(assemble_track(segments, wav_path))
        job.metrics = compute_metrics(
            job, pipeline_seconds=time.perf_counter() - started
        )
        job.status = JobStatus.done
        return job
    except Exception as exc:
        job.status = JobStatus.failed
        job.error = str(exc)
        raise
