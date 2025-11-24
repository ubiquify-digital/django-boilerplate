"""Tasks for Users"""

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@shared_task(queue="emails")
def send_otp_email(email, otp):
    """Send OTP verification email"""
    support_email = getattr(settings, "DEFAULT_FROM_EMAIL", "support@accelno.com")
    html_message = render_to_string(
        "otp_email.html",
        {
            "otp": otp,
            "support_email": support_email,
        },
    )
    plain_message = (
        f"Your OTP verification code is: {otp}\n\nThis code will expire in 10 minutes."
    )

    email_message = EmailMultiAlternatives(
        subject="OTP Verification - Accelno",
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    email_message.attach_alternative(html_message, "text/html")
    email_message.send(fail_silently=False)
