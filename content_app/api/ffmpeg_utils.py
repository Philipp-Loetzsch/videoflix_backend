from pathlib import Path
import subprocess
from content_app.models import Video
from django.conf import settings


def run_ffmpeg_task(video_id, target_subdir, filename_suffix, ffmpeg_args, model_field):
    video = Video.objects.get(id=video_id)
    source_path = Path(video.file.path)
    filename = source_path.stem
    out_dir = source_path.parent / target_subdir
    out_dir.mkdir(parents=True, exist_ok=True)

    output_path = out_dir / f"{filename}_{filename_suffix}"
    subprocess.run(ffmpeg_args(source_path, output_path), capture_output=True)

    relative_path = output_path.relative_to(Path(settings.MEDIA_ROOT))
    setattr(video, model_field, str(relative_path))
    video.save(update_fields=[model_field])
