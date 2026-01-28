from django.db import models
from django.forms import ValidationError
from parler.models import TranslatableModel, TranslatedFields
from apps.utils.models import AbstractBaseUUID, AbstractTimeStamped
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField


class Exercise(AbstractBaseUUID, AbstractTimeStamped, TranslatableModel):
    RESOLUTION_CHOICES = [
        ("repetition", _("Repetition")),  # ex: 10 push-ups
        ("duration", _("Duration")),  # ex: 30 sec plank
    ]

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
    PRACTICE_ZONE_CHOICES = [
        ("everywhere", "Everywhere"),
        ("climbing_gym", "Climbing Gym"),
    ]
    practice_zone = models.CharField(
        max_length=20, choices=PRACTICE_ZONE_CHOICES, default="everywhere"
    )
    image = models.ImageField(upload_to="exercises/images/", blank=True, null=True)
    gif = models.FileField(upload_to="exercises/gifs/", blank=True, null=True)
    video = models.URLField(blank=True, null=True)
    resolution = models.CharField(
        max_length=20,
        choices=RESOLUTION_CHOICES,
        default="repetition",
        help_text=_("Does this exercise count by repetitions or seconds?"),
    )

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
    FOCUS_CHOICES = [
        ("general_fitness", _("General Fitness")),
        ("climbing_performance", _("Climbing Performance")),
    ]
    LEVEL_CHOICES = [
        ("beginner", _("Beginner")),
        ("intermediate", _("Intermediate")),
        ("advanced", _("Advanced")),
    ]
    FOCUS_AXIS_CHOICES = [
        # Climbing - Technique / Tactics
        ("technical_bouldering", _("Technical bouldering")),
        ("project_bouldering", _("Project bouldering")),
        ("route_technique", _("Route technique")),
        ("movement_quality", _("Movement quality")),
        ("coordination", _("Coordination")),
        ("footwork", _("Footwork")),
        # Climbing - Performance
        ("power", _("Power")),
        ("max_strength", _("Max strength")),
        ("power_endurance", _("Power endurance")),
        ("endurance_continuity", _("Endurance / continuity")),
        ("climbing_volume", _("Climbing volume")),
        # Specific climbing training
        ("finger_strength", _("Finger strength")),
        ("upper_body_strength", _("Upper body strength")),
        ("core_tension", _("Core tension")),
        ("lock_off_strength", _("Lock-off strength")),
        ("pulling_strength", _("Pulling strength")),
        # General physical preparation (bodyweight)
        ("general_strength", _("General strength")),
        ("mobility", _("Mobility")),
        ("stability", _("Stability")),
        ("balance", _("Balance")),
        ("conditioning", _("Conditioning")),
        # Recovery / Health
        ("active_recovery", _("Active recovery")),
        ("injury_prevention", _("Injury prevention")),
        ("antagonist_training", _("Antagonist training")),
        # Methodology
        ("progressive_overload", _("Progressive overload")),
        ("deload", _("Deload / recovery")),
        ("movement_efficiency", _("Movement efficiency")),
    ]

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
    focus = models.CharField(
        max_length=20, choices=FOCUS_CHOICES, default="general_fitness"
    )
    level = models.CharField(
        max_length=20, choices=LEVEL_CHOICES, default="intermediate"
    )
    duration_days = models.PositiveIntegerField(
        default=14, help_text="Duration of program in days"
    )
    is_public = models.BooleanField(default=False)
    content = models.JSONField(blank=True, default=dict)
    focus_axes = ArrayField(
        models.CharField(max_length=50, choices=FOCUS_AXIS_CHOICES),
        default=list,
        blank=True,
    )
    cycle_rhythm = models.JSONField(blank=True, default=dict)

    def _validate_and_prepare(self):
        """
        Centralizes validation and preparation before saving the instance.
        """
        # ----------------- SLUG -----------------
        if not self.slug:
            en_name = self.safe_translation_getter("name", language_code="en")
            if isinstance(en_name, str) and en_name.strip():
                self.slug = slugify(en_name).replace("-", "_")

        # ----------------- CONTENT -----------------
        content = self.content or {}
        if "version" not in content:
            raise ValidationError("Program content must define a 'version'.")

        sessions = content.get("sessions")
        if not isinstance(sessions, list) or not sessions:
            raise ValidationError(
                "Program content must contain a non-empty list of sessions."
            )

        exercise_slugs = set()
        for session_idx, session in enumerate(sessions):
            sequences = session.get("sequences", [])

            # New rule: validate that climbing_gym series are grouped together
            practice_zones = []
            for sequence in sequences:
                for item in sequence:
                    # Validate exercise slug and value
                    slug = item.get("exercise")
                    if not isinstance(slug, str):
                        raise ValidationError(
                            "Each exercise item must define an 'exercise' slug."
                        )
                    value = item.get("value")
                    if not isinstance(value, (int, float)):
                        raise ValidationError(
                            f"Exercise '{slug}' must define a numeric 'value'."
                        )
                    exercise_slugs.add(slug)

                    # Collect practice_zone (fallback to session zone if missing)
                    zone = item.get("practice_zone") or session.get("zone")
                    practice_zones.append(zone)

            # Validate climbing_gym grouping
            # Convert zones to flags: 1 = climbing_gym, 0 = other
            zone_flags = [1 if z == "climbing_gym" else 0 for z in practice_zones]
            # Detect interruption: 1…0…1 pattern is invalid
            in_climbing_block = False
            seen_non_climbing_after_climbing = False
            for flag in zone_flags:
                if flag == 1:
                    if seen_non_climbing_after_climbing:
                        raise ValidationError(
                            f"Session {session_idx + 1}: climbing_gym series must be grouped together."
                        )
                    in_climbing_block = True
                elif flag == 0:
                    if in_climbing_block:
                        seen_non_climbing_after_climbing = True

        # ----------------- CHECK EXERCISES EXIST -----------------
        existing_slugs = set(
            Exercise.objects.filter(slug__in=exercise_slugs).values_list(
                "slug", flat=True
            )
        )
        print(existing_slugs)
        missing = exercise_slugs - existing_slugs
        if missing:
            raise ValidationError(
                f"Unknown exercise slugs in program content: {missing}"
            )

        # ----------------- AUTO-COMPUTE DURATION -----------------
        repeat = content.get("repeat", {})
        cycles = repeat.get("cycles", 1) if isinstance(repeat, dict) else 1
        self.duration_days = len(sessions) * cycles

    def save(self, *args, **kwargs):
        self._validate_and_prepare()
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
            program._validate_and_prepare()
            instances.append(program)

        cls.objects.bulk_create(instances)
        return instances
