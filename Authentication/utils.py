from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

def send_verification_email(user):
    token = str(RefreshToken.for_user(user).access_token)
    verification_url = f"{"settings.FRONTEND_URL"}/api/v1/verify-email/?token={token}"
    send_mail(
        'Verify your email',
        f'Click the link to verify your account: {verification_url}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )

def send_password_reset_email(user):
    token = str(RefreshToken.for_user(user).access_token)
    reset_url = f"{"settings.FRONTEND_URL"}/api/v1/reset-password/?token={token}"
    send_mail(
        'Reset your password',
        f'Click the link to reset your password: {reset_url}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )