from apps.programs.choices import Focus, FocusAxis, Level, PracticeZone, Resolution
from apps.programs.services.program_validator import ProgramDataValidator
from django.db import models
from django.core.exceptions import ValidationError
from parler.models import TranslatableModel, TranslatedFields
from apps.utils.models import AbstractBaseUUID, AbstractTimeStamped
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField


class Exercise(AbstractBaseUUID, AbstractTimeStamped, TranslatableModel):

    resolution = models.CharField(
        max_length=20,
        choices=Resolution.choices,
        default=Resolution.REPETITION,
        help_text=_("Does this exercise count by repetitions or seconds?"),
        db_index=True,
    )

    practice_zone = models.CharField(
        max_length=20,
        choices=PracticeZone.choices,
        default=PracticeZone.EVERYWHERE,
        db_index=True,
    )

    translations = TranslatedFields(
        name=models.CharField(_("Name"), max_length=200),
        description=models.TextField(_("Description"), blank=True),
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="Slugified version of the English name, auto-generated",
    )

    image = models.ImageField(upload_to="exercises/images/", blank=True, null=True)
    gif = models.FileField(upload_to="exercises/gifs/", blank=True, null=True)
    video = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # -------------------------------------------------
        # SLUG (EN only, safe for pylance / typing)
        # -------------------------------------------------
        if not self.slug:
            en_name = self.safe_translation_getter("name", language_code="en")
            if isinstance(en_name, str) and en_name.strip():
                self.slug = slugify(en_name).replace("-", "_")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or str(self.id)


class Program(AbstractBaseUUID, AbstractTimeStamped, TranslatableModel):

    focus = models.CharField(
        max_length=32,
        choices=Focus.choices,
        default=Focus.GENERAL_FITNESS,
        db_index=True,
    )

    level = models.CharField(
        max_length=32,
        choices=Level.choices,
        default=Level.INTERMEDIATE,
        db_index=True,
    )

    focus_axes = ArrayField(
        models.CharField(
            max_length=50,
            choices=FocusAxis.choices,
        ),
        default=list,
        blank=True,
    )

    translations = TranslatedFields(
        name=models.CharField(_("Name"), max_length=200),
        description=models.TextField(_("Description"), blank=True),
        realistic_if=models.JSONField(blank=True, default=list),
        not_realistic_if=models.JSONField(blank=True, default=list),
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="Slugified version of the English name, auto-generated",
    )

    duration_days = models.PositiveIntegerField(
        default=14, help_text="Duration of program in days"
    )
    is_public = models.BooleanField(default=False)
    content = models.JSONField(blank=True, default=dict)

    cycle_rhythm = models.JSONField(blank=True, default=dict)


    def save(self, *args, **kwargs):
        ProgramDataValidator(self).validate_and_prepare()
        super().save(*args, **kwargs)


    @classmethod
    def bulk_create_from_json(cls, json_list: list) -> list:
        """
        Bulk create Program from json fixtures.
        Each node is verify using _validate_and_prepare.
        """
        instances = []
        for data in json_list:
            translations = data.pop("translations", {})
            program = cls(
                focus=data.get("focus"),
                level=data.get("level"),
                content=data,
                is_public=data.get("is_public", False),
            )
            # set translations
            for lang, fields in translations.items():
                for field, value in fields.items():
                    program.set_current_language(lang)
                    setattr(program, field, value)
            ProgramDataValidator(program).validate_and_prepare()
            instances.append(program)

        cls.objects.bulk_create(instances)
        return instances
