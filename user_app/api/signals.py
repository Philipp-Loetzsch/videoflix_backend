from django.core.mail import send_mail
from django.db.models.signals import post_save
import django_rq
from django.dispatch import receiver

