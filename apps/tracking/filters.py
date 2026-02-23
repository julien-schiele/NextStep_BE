import django_filters
from .models import UserProgram
from .choices import Status


class UserProgramFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(
        field_name="status",
        choices=Status.choices,
    )
    program = django_filters.UUIDFilter(field_name="program_id")

    class Meta:
        model = UserProgram
        fields = ["status", "program"]
