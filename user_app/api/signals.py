from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django_rq import enqueue
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from pathlib import Path
from django.core.signing import TimestampSigner
from email.mime.image import MIMEImage
from pathlib import Path
from .views import send_reset_email_signal
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()
signer = TimestampSigner()
  
def send_activation_email(user_id):
    """Send activation email to new user."""
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = f"{settings.FRONTEND_URL}/activate/{uidb64}/{token}"

    html_content = render_to_string("emails/account_activation.html", {
        "user": user,
        "activation_link": activation_link
    })

    email = EmailMultiAlternatives(
        subject="Activate your account",
        body="Please activate your account by clicking on the button.",
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
    """Queue activation email for new users."""
    if created and not instance.is_active:
        enqueue(send_activation_email, instance.id)


@receiver(send_reset_email_signal)
def send_reset_password_email(sender, user, **kwargs):
    """Send password reset email with token link."""
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_link = f"{settings.FRONTEND_URL}/reset_password/{uidb64}/{token}"

    html_content = render_to_string("emails/password_reset.html", {
        "user": user,
        "reset_link": reset_link,
    })

    email = EmailMultiAlternatives(
        subject="reset password",
        body="You have requested a password reset.",
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