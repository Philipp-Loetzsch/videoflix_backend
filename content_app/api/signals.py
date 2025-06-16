from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rq import enqueue
from content_app.api.tasks import convert720p
from ..models import Video

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        enqueue(convert720p, instance.file)