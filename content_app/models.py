import uuid
from django.db import models

CATEGORY_CHOICES = [
    ("Horror", "Horror"),
    ("Action", "Action"),
    ("Drama", "Drama"),
    ("Comedy", "Comedy"),
    ("Science Fiction", "Science Fiction"),
    ("Documentary", "Documentary"),
    ("Cartoon", "Cartoon"),
    ("Fantasy", "Fantasy"),
    ("Other", "Other"),
]


def video_upload_path(instance, filename):
    """
    Generate the upload path for video files.
    
    Args:
        instance: The Video model instance
        filename (str): Original filename
        
    Returns:
        str: The path where the video file should be stored
    """
    return f"videos/{instance.title}_{instance.uuid}/{filename}"


def preview_upload_path(instance, filename):
    """
    Generate the upload path for video preview files.
    
    Args:
        instance: The Video model instance
        filename (str): Original filename
        
    Returns:
        str: The path where the preview file should be stored
    """
    return f"videos/{instance.title}_{instance.uuid}/preview/{filename}"


def thumbnail_upload_path(instance, filename):
    """
    Generate the upload path for video thumbnail images.
    
    Args:
        instance: The Video model instance
        filename (str): Original filename
        
    Returns:
        str: The path where the thumbnail file should be stored
    """
    return f"videos/{instance.title}_{instance.uuid}/thumbnails/{filename}"


class Video(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255, help_text="title of the video")
    description = models.TextField(help_text="description of the video", blank=True, null=True)
    file = models.FileField(
        upload_to=video_upload_path, help_text="uploadet video file", max_length=300
    )
    hls_playlist = models.FileField(
        upload_to=video_upload_path,
        blank=True,
        null=True,
        help_text="HLS Master Playlist (.m3u8)",
        max_length=500,
    )
    duration = models.PositiveIntegerField(
        default=0, help_text="Duration in seconds", blank=True
    )
    preview = models.FileField(upload_to=preview_upload_path, max_length=255, blank=True, null=False)
    thumbnail = models.ImageField(upload_to=thumbnail_upload_path, max_length=255, blank=True, null=True, help_text="thumbnail")
    preview_title = models.CharField(max_length=50, help_text="short preview text of video e.g. Pokemon", blank=True, null=True)
    category = models.CharField(
        choices=CATEGORY_CHOICES,
        default="Other",
        help_text="Main category of the video",
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="date of creation")

    def __str__(self):
        """
        String representation of the Video model.
        
        Returns:
            str: The title and category of the video
        """
        return f"{self.title} ({self.get_category_display()})"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Video"
        verbose_name_plural = "Videos"
