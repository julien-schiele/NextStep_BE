from django.db import models
from django.utils.translation import gettext_lazy as _


class Status(models.TextChoices):
    ACTIVE = "active", _("Active")
    COMPLETED = "completed", _("Completed")
    ABANDONNED = "abandoned", _("Abandoned")


class Rating(models.TextChoices):
    TOO_EASY = "too_easy", _("Too Easy")
    OK = "ok", _("OK")
    TOO_HARD = "too_hard", _("Too Hard")


class Usefunlness(models.TextChoices):
    NOT_USEFUL = "not_useful", _("Not Useful")
    USEFUL = "useful", _("Useful")
    VERY_USEFUL = "very_useful", _("Very Useful")
