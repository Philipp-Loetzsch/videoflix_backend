from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django_rq import enqueue
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.authtoken.models import Token
from django.conf import settings

User = get_user_model()

def send_activation_email(user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    token, _ = Token.objects.get_or_create(user=user)
    activation_link = f"{settings.FRONTEND_URL}/activate/{token.key}"

    subject = "Aktiviere deinen Account"
    html_message = render_to_string("emails/account_activation.html", {
        "user": user,
        "activation_link": activation_link
    })

    send_mail(
        subject=subject,
        message="Bitte aktiviere deinen Account über den Link in der E-Mail.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message
    )

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        enqueue(send_activation_email, instance.id)
