from apps.programs.models import Program
from apps.tracking.choices import Rating, Status, Usefunlness
from apps.users.models import User
from apps.utils.models import AbstractBaseUUID, AbstractTimeStamped
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserProgram(AbstractBaseUUID, AbstractTimeStamped, models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_programs"
    )
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="user_programs"
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )

    def __str__(self):
        return f"UserProgram {self.id} ({self.status})"


class UserProgramSession(AbstractBaseUUID, AbstractTimeStamped, models.Model):

    user_program = models.ForeignKey(
        UserProgram, on_delete=models.CASCADE, related_name="sessions"
    )
    cycle_count = models.PositiveIntegerField()
    session_in_cycle = models.PositiveIntegerField()
    session_snapshot = models.JSONField()
    rating = models.CharField(
        max_length=32,
        choices=Rating.choices,
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        unique_together = ("user_program", "cycle_count", "session_in_cycle")
        ordering = ["user_program", "cycle_count", "session_in_cycle"]

    @property
    def completed(self):
        return self.rating is not None

    def __str__(self):
        return (
            f"UserProgramSessionProgress"
            f"(program={self.user_program.slug}, "
            f"cycle={self.cycle_count}, "
            f"session={self.session_in_cycle})"
        )


class UserProgramFeedback(AbstractBaseUUID, AbstractTimeStamped, models.Model):

    user_program = models.ForeignKey(
        UserProgram, on_delete=models.CASCADE, related_name="feedbacks"
    )
    usefulness = models.CharField(
        max_length=32,
        choices=Usefunlness.choices,
        null=True,
        blank=True,
        db_index=True,
    )
    would_repeat = models.BooleanField(blank=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"UserProgramFeedback {self.id} ({self.usefulness})"
