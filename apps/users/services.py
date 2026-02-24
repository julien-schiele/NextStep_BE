import uuid
from rest_framework.exceptions import ValidationError
from apps.users.choices import ActionChoices
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import UserActionToken
from django.utils.translation import gettext_lazy as _


def generate_user_action_token(user, expiration_hours, action_type):
    token = UserActionToken.objects.create(
        user=user,
        action=action_type,
        expires_at=timezone.now() + timedelta(hours=expiration_hours),
    ).token
    return token


################### P A S S W O R D   R E S E T ###################################################


def generate_reset_token(user):
    return generate_user_action_token(user, 1, ActionChoices.RESET_PASSWORD)


def send_reset_password_email(email, token):
    backend_link = f"{settings.BE_HOST_URL}/api/reset-password/{token}/"
    frontend_link = f"{settings.FE_HOST_URL}/reset-password/?token={token}"
    send_mail(
        "NextStep - Password Reset",
        f"Click the following link to reset your password: {frontend_link} TODO:JS frontend must call {backend_link}",
        "no-reply@nextstep.com",
        [email],
        fail_silently=False,
    )


def reset_password_with_token(token, new_password):
    user_action_token = (
        UserActionToken.objects.filter(
            token=token,
            action=ActionChoices.RESET_PASSWORD,
        )
        .select_related("user")
        .first()
    )

    if not user_action_token:
        raise ValidationError(_("Invalid token."))

    if user_action_token.is_expired():
        user_action_token.delete()
        raise ValidationError(_("Token expired."))

    user = user_action_token.user
    user.set_password(new_password)
    user.save()

    user_action_token.delete()

    return user
