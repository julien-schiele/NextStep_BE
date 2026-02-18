import django_filters
from .models import UserProgram
from .choices import Status


class UserProgramFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(
        field_name="status",
        choices=Status.choices,
    )

    class Meta:
        model = UserProgram
        fields = ["status"]
