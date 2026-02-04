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
        field_name="focus_axes",
        choices=FocusAxis.choices,
        lookup_expr="contains",
    )

    class Meta:
        model = Program
        fields = ["level", "focus"]
