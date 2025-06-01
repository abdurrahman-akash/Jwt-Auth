from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(user, verification_code):
    verification_url = f"{settings.BACKEND_URL}/api/v1/verify-email/?code={verification_code}"
    subject = 'Verify your email'
    message = f'Click the link to verify your account: {verification_url}'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=f'<p>Click <a href="{verification_url}">here</a> to verify your email.</p>',
        fail_silently=False,
    )

def send_password_reset_email(user, reset_token):
    reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token}"
    subject = 'Reset your password'
    message = f'Click the link to reset your password: {reset_url}'
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=f'<p>Click <a href="{reset_url}">here</a> to reset your password.</p>',
        fail_silently=False,
    )