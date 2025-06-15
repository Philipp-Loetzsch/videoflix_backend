import uuid
from django.db import models

CATEGORY_CHOICES = [
    ('HOR', 'Horror'),
    ('ACT', 'Action'),
    ('DRA', 'Drama'),
    ('COM', 'Comedy'),
    ('SCI', 'Science Fiction'),
    ('DOC', 'Documentary'),
    ('OTH', 'Other'),
]

# Uploadpfade mit title + uuid
def video_upload_path(instance, filename):
    return f"videos/{instance.title}_{instance.uuid}/{filename}"

def preview_upload_path(instance, filename):
    return f"videos/{instance.title}_{instance.uuid}/preview/{filename}"

def thumbnail_upload_path(instance, filename):
    return f"videos/{instance.title}_{instance.uuid}/thumbnails/{filename}"

class Video(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255, help_text="Titel des Videos")
    description = models.TextField(help_text="Beschreibung des Inhalts")
    file = models.FileField(upload_to=video_upload_path, help_text="Hochgeladene Videodatei")
    duration = models.PositiveIntegerField(default=0, help_text="Dauer in Sekunden", blank=True)
    preview = models.FileField(upload_to=preview_upload_path)
    thumbnail = models.ImageField(
        upload_to=thumbnail_upload_path,
        blank=True,
        null=True,
        help_text="Vorschaubild"
    )
    category = models.CharField(
        max_length=3,
        choices=CATEGORY_CHOICES,
        default='OTH',
        help_text="Hauptkategorie"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Erstellungsdatum")

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
