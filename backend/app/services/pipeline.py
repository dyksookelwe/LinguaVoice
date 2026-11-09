import time
from pathlib import Path

from app.audio.align import align_segment
from app.audio.convert import convert_to_wav, make_voice_reference
from app.audio.export import assemble_track, export_mp3
from app.audio.validate import validate_audio
from app.schemas.job import Job, JobStatus
from app.services.metrics import compute_metrics, write_metrics
from app.services.synthesize import synthesize_segment
from app.services.transcribe import transcribe_and_segment
from app.services.translate import is_text_too_long, translate_segment


def run_pipeline(job: Job) -> Job:
    """Run the dubbing steps in order. Each step is a named function."""
    started = time.perf_counter()
    job.status = JobStatus.processing
    try:
        validated = validate_audio(Path(job.source_path))
        wav_path = convert_to_wav(validated)
        voice_ref = make_voice_reference(validated)
        job.reference_wav_path = str(voice_ref)

        segments = transcribe_and_segment(wav_path)
        for segment in segments:
            segment.src_duration = segment.duration
            segment.tgt_text = translate_segment(
                segment.src_text, segment.src_duration
            )
            segment.text_too_long = is_text_too_long(
                segment.tgt_text, segment.src_duration
            )
        
            segment.audio_path = str(
                synthesize_segment(segment, voice_ref, use_cloning=True)
            )
            align_segment(segment)

        job.segments = segments
        dubbed_wav = assemble_track(segments, wav_path)
        job.output_path = str(dubbed_wav)
        job.output_mp3_path = str(export_mp3(dubbed_wav))
        job.metrics = compute_metrics(
            job, pipeline_seconds=time.perf_counter() - started
        )
        write_metrics(job.metrics, dubbed_wav.parent / "metrics.json")
        job.status = JobStatus.done
        return job
    except Exception as exc:
        job.status = JobStatus.failed
        job.error = str(exc)
        raise
