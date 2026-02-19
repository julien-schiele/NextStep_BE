from django.db import models
from django.utils.translation import gettext_lazy as _


class ActionChoices(models.TextChoices):
    RESET_PASSWORD = "reset_password", _("Reset password")
