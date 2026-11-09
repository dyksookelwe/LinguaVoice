import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.schemas.job import Job  # noqa: E402
from app.services.pipeline import run_pipeline  # noqa: E402

BACKEND = Path(__file__).resolve().parents[2]
SOURCE = BACKEND / "scripts" / "samples_raw" / "sk_long.mp3"
WORK = BACKEND / "var" / "demo"

WORK.mkdir(parents=True, exist_ok=True)
source = WORK / "source.mp3"
shutil.copy(SOURCE, source)

job = run_pipeline(Job(id="demo", source_path=str(source)))

print("статус:", job.status.value)
for s in job.segments:
    print(
        f"{s.id}: voice={s.voice} окно={s.src_duration:.1f}с "
        f"озвучка={s.gen_duration:.1f}с ratio={s.stretch_ratio:.2f} "
        f"сдвиг={s.placed_start - s.start:+.2f}с"
    )
    print(f"    {s.src_text}  ->  {s.tgt_text}")
print("\nметрики:", job.metrics.model_dump())
print("WAV:", job.output_path)
print("MP3:", job.output_mp3_path)