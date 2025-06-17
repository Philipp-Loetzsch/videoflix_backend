import os
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import django_rq
from content_app.api.tasks import convert720p
from ..models import Video
import shutil
import time

# def wait_for_file(path, attempts=1000, delay=0.01):
#     for _ in range(attempts):
#         if os.path.exists(path):
#             print(f"Datei gefunden: {path}")
#             return True
#         time.sleep(delay)
#     return False


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        # if not wait_for_file(instance.file.path):
        #     print(f"Datei nicht gefunden: {instance.file.path}")
        #     return
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert720p, instance.file.path)
        
@receiver(post_delete, sender=Video)
def delete_folder_on_model_delete(sender, instance, **kwargs):
    if instance.file:
        folder_path = os.path.dirname(instance.file.path)
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)