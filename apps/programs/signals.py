from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from apps.programs.models import Exercise, Program


@receiver(pre_delete, sender=Exercise)
def prevent_exercise_deletion_if_used(sender, instance: Exercise, **kwargs):
    """
    Prevent deletion of an Exercise if it is referenced
    in any Program.content.sessions[].sequences[].exercise
    """
    slug = instance.slug
    if not slug:
        return

    programs = Program.objects.all().only("id", "content")

    used_in = []

    for program in programs:
        content = program.content or {}
        sessions = content.get("sessions", [])

        for session in sessions:
            for sequence in session.get("sequences", []):
                for item in sequence:
                    if item.get("exercise") == slug:
                        used_in.append(program.slug or str(program.id))
                        break

    if used_in:
        raise ValidationError(
            _("Cannot delete exercise '%(slug)s': used in program(s): %(used_in)s")
            % {"slug": slug, "used_in": ", ".join(used_in)}
        )
