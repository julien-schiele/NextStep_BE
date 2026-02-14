import django_filters
from .models import Program
from .choices import Focus, FocusAxis, Level


class ProgramFilter(django_filters.FilterSet):
    level = django_filters.ChoiceFilter(
        field_name="level",
        choices=Level.choices,
    )
    focus = django_filters.ChoiceFilter(
        field_name="focus",
        choices=Focus.choices,
    )

    focus_axes = django_filters.MultipleChoiceFilter(
        choices=FocusAxis.choices,
        method="filter_focus_axes",
    )

    def filter_focus_axes(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(focus_axes__overlap=value)

    class Meta:
        model = Program
        fields = ["level", "focus"]
