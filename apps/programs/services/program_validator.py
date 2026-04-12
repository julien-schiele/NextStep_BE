from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from pydantic import ValidationError as PydanticValidationError

from apps.programs.schemas import ProgramContent


class ProgramDataValidator:
    def __init__(self, program):
        self.program = program
        self.raw_content = program.content or {}
        self.parsed_content: ProgramContent | None = None

    # ----------------- PUBLIC API -----------------

    def validate_and_prepare(self):
        self._set_slug_if_needed()
        self._parse_content()
        exercise_slugs = self._validate_sessions()
        self._validate_exercises_exist(exercise_slugs)
        self._compute_duration()
        self._validate_focus_axes()

    # ----------------- SLUG -----------------

    def _set_slug_if_needed(self):
        if not self.program.slug:
            en_name = self.program.safe_translation_getter("name", language_code="en")
            if isinstance(en_name, str) and en_name.strip():
                self.program.slug = slugify(en_name).replace("-", "_")

    # ----------------- PYDANTIC PARSING -----------------

    def _parse_content(self):
        try:
            self.parsed_content = ProgramContent(**self.raw_content)
        except PydanticValidationError as e:
            # Convertir les erreurs Pydantic en liste de strings
            messages = []
            for err in e.errors():
                loc = ".".join(str(l) for l in err['loc'])
                messages.append(f"{loc}: {err['msg']}")
            raise ValidationError(messages)

    # ----------------- SESSIONS -----------------
    
    def _validate_sessions(self) -> set[str]:
        exercise_slugs = set()

        if self.parsed_content:
            for session_idx, session in enumerate(self.parsed_content.sessions):
                practice_zones = []

                for sequence in session.sequences:
                    for item in sequence:
                        # ----------------- EXERCISE SLUG -----------------
                        # Pydantic garantit que c'est un string et que value est float
                        exercise_slugs.add(item.exercise)

                        # ----------------- PRACTICE ZONE -----------------
                        # fallback sur session.zone si item.practice_zone absent
                        zone = item.practice_zone or session.zone
                        practice_zones.append(zone)

                self._validate_climbing_grouping(practice_zones, session_idx)

        return exercise_slugs

    # ----------------- BUSINESS RULE -----------------

    def _validate_climbing_grouping(self, practice_zones, session_idx):
        zone_flags = [1 if z == "climbing_gym" else 0 for z in practice_zones]

        in_climbing_block = False
        seen_non_climbing_after_climbing = False

        for flag in zone_flags:
            if flag == 1:
                if seen_non_climbing_after_climbing:
                    raise ValidationError(
                        _(
                            "Session '%(i)s': climbing_gym series must be grouped together."
                        )
                        % {"i": session_idx + 1}
                    )
                in_climbing_block = True
            elif flag == 0:
                if in_climbing_block:
                    seen_non_climbing_after_climbing = True

    # ----------------- DB VALIDATION -----------------

    def _validate_exercises_exist(self, exercise_slugs):
        from ..models import Exercise

        existing_slugs = set(
            Exercise.objects.filter(slug__in=exercise_slugs).values_list(
                "slug", flat=True
            )
        )

        missing = exercise_slugs - existing_slugs
        if missing:
            raise ValidationError(
                _("Unknown exercise slugs in program content: '%(missing)s'")
                % {"missing": missing}
            )

    # ----------------- COMPUTED FIELDS -----------------

    def _compute_duration(self):
        if not self.parsed_content:
            raise ValidationError(_("Program content not parsed"))
        sessions = self.parsed_content.sessions
        cycles = self.parsed_content.repeat.cycles if self.parsed_content.repeat else 1
        self.program.duration_days = len(sessions) * cycles

    # ----------------- FOCUS AXES -----------------

    def _validate_focus_axes(self):
        from ..models import FocusAxis

        valid_axes = {c[0] for c in FocusAxis.choices}
        invalid = set(self.program.focus_axes) - valid_axes

        if invalid:
            raise ValidationError(
                _("Invalid focus_axes: '%(invalid)s'") % {"invalid": invalid}
            )
