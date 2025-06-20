import os
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import django_rq
from content_app.api.tasks import convert_to_hls, create_thumbnail, create_preview
from ..models import Video
import shutil
import time

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        queue = django_rq.get_queue('default', autocommit=True)
        video_id = instance.id

        queue.enqueue(convert_to_hls, video_id)
        queue.enqueue(create_thumbnail, video_id)
        queue.enqueue(create_preview, video_id)


        
@receiver(post_delete, sender=Video)
def delete_folder_on_model_delete(sender, instance, **kwargs):
    if instance.file:
        folder_path = os.path.dirname(instance.file.path)
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)