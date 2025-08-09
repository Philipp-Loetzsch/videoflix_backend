import os
import subprocess
from pathlib import Path
from content_app.models import Video
from core import settings
from .ffmpeg_utils import run_ffmpeg_task
import ffmpeg

def _get_video_and_paths(video_id: int):
    """
    Loads the Video object and creates the necessary file paths.
    Returns the Video object, source path, and HLS folder
    or None values on errors.
    """
    try:
        video = Video.objects.get(id=video_id)
        source_path = Path(video.file.path)
        if not source_path.exists():
            return None, None, None
    except Video.DoesNotExist:
        return None, None, None
    
    hls_dir = source_path.parent / "hls"
    hls_dir.mkdir(exist_ok=True)
    return video, source_path, hls_dir

def _probe_video_metadata(source_path: Path):
    """
    Probes the video file for metadata like resolution and duration.
    Returns the metadata as a tuple or None on errors.
    """
    try:
        probe = ffmpeg.probe(str(source_path))
        video_stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
        source_width = int(video_stream["width"])
        source_height = int(video_stream["height"])
        duration_seconds = float(probe['format']['duration'])
        return source_width, source_height, duration_seconds
    except (ffmpeg.Error, StopIteration, ValueError, KeyError) as e:
        return None

def _process_resolution(source_path: Path, hls_dir: Path, label: str, opts: dict, source_dims: tuple):
    """
    Converts the video to a specific resolution and bitrate.
    Returns a dictionary with playlist data or None on errors/skipping.
    """
    source_width, source_height = source_dims
    target_width, target_height = map(int, opts["scale"].split("x"))

    # Skip conversion if the target resolution is higher than the source
    if source_width < target_width or source_height < target_height:
        return None

    try:
        output_file = hls_dir / f"{label}.m3u8"
        segment_path = hls_dir / f"{label}_%03d.ts"
        
        # Select video and audio streams explicitly
        stream = ffmpeg.input(str(source_path))
        video_stream = stream.video
        audio_stream = stream.audio

        # Process the video stream
        video_processed = (
            video_stream
            .filter('scale', target_width, target_height, force_original_aspect_ratio='decrease')
            .filter('pad', target_width, target_height, '(ow-iw)/2', '(oh-ih)/2')
        )
        
        # Combine video and audio streams into the output
        (
            ffmpeg
            .output(
                video_processed,
                audio_stream,
                str(output_file),
                vcodec='libx264', acodec='aac', **{'b:v': opts['bitrate'], 'profile:v': 'main', 'sc_threshold': 0, 'g': 48,
                                                  'keyint_min': 48, 'hls_time': 4, 'hls_playlist_type': 'vod',
                                                  'hls_segment_filename': str(segment_path), 'ar': 48000,
                                                  'b:a': '128k', 'maxrate': opts['bitrate'], 'bufsize': '4200k'}
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return {"resolution": opts["scale"], "bandwidth": opts["bitrate"].replace("k", "000"), "filename": f"{label}.m3u8"}
    except ffmpeg.Error as e:
        return None

def _create_master_playlist(hls_dir: Path, playlist_entries: list):
    """
    Creates the master playlist file from all generated playlists.
    """
    if not playlist_entries:
        return None
        
    master_path = hls_dir / "master.m3u8"
    with master_path.open("w") as f:
        f.write("#EXTM3U\n")
        f.write("#EXT-X-VERSION:3\n")
        for entry in playlist_entries:
            f.write(f'#EXT-X-STREAM-INF:BANDWIDTH={entry["bandwidth"]},RESOLUTION={entry["resolution"]}\n')
            f.write(f'{entry["filename"]}\n')
    return master_path

def _update_django_model(video, master_path: Path, duration: float):
    """
    Updates the Django model with the paths and duration.
    """
    media_root = Path(settings.MEDIA_ROOT)
    relative_path = master_path.relative_to(media_root)

    video.hls_playlist.name = str(relative_path)
    video.duration = int(duration)
    video.save(update_fields=["hls_playlist", "duration"])

def convert_to_hls(video_id: int):
    """
    Orchestrates the entire HLS conversion process.
    
    Converts a video file to HLS format with multiple quality levels.
    Creates a master playlist and individual stream playlists.
    
    Args:
        video_id (int): The ID of the Video model instance to convert
        
    Note:
        - Generates streams for 360p, 480p, 720p, and 1080p if source resolution allows
        - Skips resolutions higher than the source video
        - Creates HLS segments and playlists in a 'hls' subdirectory
        - Updates the Video model with the master playlist path and duration
    """
    video, source_path, hls_dir = _get_video_and_paths(video_id)
    if not video:
        return

    if source_path.suffix.lower() == '.webp':
        return
        
    metadata = _probe_video_metadata(source_path)
    if not metadata:
        return
    source_width, source_height, duration_seconds = metadata

    resolutions = {
        "360p": {"scale": "640x360", "bitrate": "800k"},
        "480p": {"scale": "854x480", "bitrate": "1400k"},
        "720p": {"scale": "1280x720", "bitrate": "2800k"},
        "1080p": {"scale": "1920x1080", "bitrate": "5000k"},
    }
    
    playlist_entries = []
    for label, opts in resolutions.items():
        entry = _process_resolution(source_path, hls_dir, label, opts, (source_width, source_height))
        if entry:
            playlist_entries.append(entry)

    master_path = _create_master_playlist(hls_dir, playlist_entries)
    if master_path:
        _update_django_model(video, master_path, duration_seconds)

def create_thumbnail(video_id):
    """
    Create a thumbnail image from a video.
    
    Takes a frame at 5 seconds into the video and saves it as a JPEG image.
    
    Args:
        video_id (int): The ID of the Video model instance
        
    Note:
        - Creates thumbnails in a 'thumbnails' subdirectory
        - Skips if thumbnail already exists
        - Updates the Video model's thumbnail field
    """
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

def get_video_resolution(path: Path) -> tuple[int, int]:
    """
    Get the resolution (width and height) of a video file.
    
    Args:
        path (Path): Path to the video file
        
    Returns:
        tuple[int, int]: A tuple containing (width, height) in pixels
    """
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

def get_video_duration(path: Path) -> float:
    """
    Get the duration of a video file in seconds.
    
    Args:
        path (Path): Path to the video file
        
    Returns:
        float: The duration of the video in seconds
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

def create_preview(video_id):
    """
    Create a 20-second preview video clip.
    
    Creates a preview starting at 25% of the video duration,
    scaled to either 1080p or 720p depending on source resolution.
    
    Args:
        video_id (int): The ID of the Video model instance
        
    Note:
        - Creates previews in a 'preview' subdirectory
        - Skips if preview already exists
        - Updates the Video model's preview field
        - Uses H.264 video codec and AAC audio codec
    """
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
