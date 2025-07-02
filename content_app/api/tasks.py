import os
import subprocess
from pathlib import Path
from content_app.models import Video
from core import settings
from .ffmpeg_utils import run_ffmpeg_task

def get_video_duration(path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

def get_video_resolution(path: Path) -> tuple[int, int]:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    width, height = map(int, result.stdout.strip().split(','))
    return width, height

def convert_to_hls(video_id):
    video = Video.objects.get(id=video_id)
    source_path = video.file.path
    base_dir = os.path.dirname(source_path)
    hls_dir = os.path.join(base_dir, "hls")
    os.makedirs(hls_dir, exist_ok=True)

    resolutions = {
        "480p": {"scale": "854:480", "bitrate": "1400k"},
        "720p": {"scale": "1280:720", "bitrate": "2800k"},
        "1080p": {"scale": "1920:1080", "bitrate": "5000k"},
    }

    playlist_entries = []
    for label, opts in resolutions.items():
        out_path = os.path.join(hls_dir, f"{label}.m3u8")
        segment_path = os.path.join(hls_dir, f"{label}_%03d.ts")
        vf_filter = (
            f"scale={opts['scale']}:force_original_aspect_ratio=decrease,"
            f"pad={opts['scale']}:(ow-iw)/2:(oh-ih)/2"
        )
        cmd = [
            "ffmpeg",
            "-i", source_path,
            "-vf", vf_filter,
            "-c:a", "aac",
            "-ar", "48000",
            "-c:v", "h264",
            "-profile:v", "main",
            "-crf", "20",
            "-sc_threshold", "0",
            "-g", "48",
            "-keyint_min", "48",
            "-b:v", opts["bitrate"],
            "-maxrate", opts["bitrate"],
            "-bufsize", "4200k",
            "-b:a", "128k",
            "-hls_time", "4",
            "-hls_playlist_type", "vod",
            "-hls_segment_filename", segment_path,
            out_path,
        ]
        subprocess.run(cmd, capture_output=True)
        playlist_entries.append({
            "resolution": opts["scale"],
            "bandwidth": opts["bitrate"].replace("k", "000"),
            "filename": f"{label}.m3u8",
        })

    create_master_path(hls_dir, playlist_entries, source_path)

def create_master_path(hls_dir, playlist_entries, source_path):
    master_path = Path(hls_dir) / "master.m3u8"
    with master_path.open("w") as f:
        f.write("#EXTM3U\n")
        for entry in playlist_entries:
            f.write(
                f'#EXT-X-STREAM-INF:BANDWIDTH={entry["bandwidth"]},RESOLUTION={entry["resolution"]}\n'
            )
            f.write(f'{entry["filename"]}\n')

    media_root = Path(settings.MEDIA_ROOT)
    relative_path = master_path.relative_to(media_root)
    video_file_rel = Path(source_path).relative_to(media_root)

    video = Video.objects.get(file=str(video_file_rel))
    video.hls_playlist.name = str(relative_path)

    duration_seconds = get_video_duration(source_path)
    video.duration = int(duration_seconds)
    video.save(update_fields=["hls_playlist", "duration"])

def create_thumbnail(video_id):
    video = Video.objects.get(id=video_id)
    source = Path(video.file.path)
    thumbnail_dir = source.parent / "thumbnails"

    if thumbnail_dir.exists() and any(thumbnail_dir.iterdir()):
        return

    def args(source, target):
        return [
            "ffmpeg",
            "-ss", "00:00:05",
            "-i", str(source),
            "-vframes", "1",
            "-q:v", "2",
            str(target),
        ]

    run_ffmpeg_task(
        video_id=video_id,
        target_subdir="thumbnails",
        filename_suffix="thumb.jpg",
        ffmpeg_args=args,
        model_field="thumbnail",
    )

def create_preview(video_id):
    video = Video.objects.get(id=video_id)
    source = Path(video.file.path)
    preview_dir = source.parent / "preview"

    if preview_dir.exists() and any(preview_dir.iterdir()):
        return

    duration = get_video_duration(source)
    start_time = int(duration * 0.25)
    width, height = get_video_resolution(source)
    target_width, target_height = (1920, 1080) if width >= 1280 else (1280, 720)
    vf_filter = (
        f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
        f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2"
    )

    def args(source, target):
        return [
            "ffmpeg", "-ss", str(start_time), "-i", str(source),
            "-t", "20",
            "-vf", vf_filter,
            "-c:v", "libx264", "-c:a", "aac", str(target)
        ]

    run_ffmpeg_task(
        video_id=video_id,
        target_subdir="preview",
        filename_suffix="preview.mp4",
        ffmpeg_args=args,
        model_field="preview",
    )
