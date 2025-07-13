from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django_rq import enqueue
from django.template.loader import render_to_string
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from rest_framework.authtoken.models import Token
from pathlib import Path
from mimetypes import guess_type
from django.core.signing import TimestampSigner
from email.mime.image import MIMEImage
from pathlib import Path

User = get_user_model()
signer = TimestampSigner()
  
def send_activation_email(user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    token = signer.sign(user.pk)
    activation_link = f"{settings.FRONTEND_URL}/activate/{token}"

    html_content = render_to_string("emails/account_activation.html", {
        "user": user,
        "activation_link": activation_link
    })

    email = EmailMultiAlternatives(
        subject="Aktiviere deinen Account",
        body="Bitte aktiviere deinen Account, indem du auf den Button klickst.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.attach_alternative(html_content, "text/html")
    image_path = Path(settings.BASE_DIR) / "templates" / "emails" / "logo.png"
    if image_path.exists():
        with open(image_path, "rb") as img:
            mime_img = MIMEImage(img.read())
            mime_img.add_header("Content-ID", "<logo_img>")
            mime_img.add_header("Content-Disposition", "inline", filename="logo.png")
            email.attach(mime_img)

    email.send()

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        enqueue(send_activation_email, instance.id)
