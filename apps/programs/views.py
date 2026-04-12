from rest_framework import viewsets, permissions, views, mixins
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .choices import Focus, Level, FocusAxis, PracticeZone, Resolution
from .models import Program, Exercise
from .serializers import (
    ExerciseFiltersSerializer,
    ProgramFiltersSerializer,
    ProgramListSerializer,
    ProgramDetailSerializer,
    ExerciseSerializer,
    ProgramSerializer,
)
from .filters import ProgramFilter
from drf_spectacular.utils import extend_schema
from itertools import chain


###################################################################################################
# PROGRAM
###################################################################################################
class ProgramViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProgramFilter

    def get_queryset(self):
        return Program.objects.filter(is_public=True)

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_serializer_class(self):
        if self.action == "list":
            return ProgramListSerializer
        if self.action == "retrieve":
            return ProgramDetailSerializer
        return ProgramSerializer


###################################################################################################
# PROGRAM FILTERS
###################################################################################################
class ProgramFiltersView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses=ProgramFiltersSerializer)
    def get(self, request, *args, **kwargs):
        used_levels = Program.objects.values_list("level", flat=True).distinct()
        used_focuses = Program.objects.values_list("focus", flat=True).distinct()
        used_focus_axes = set(
            chain.from_iterable(
                Program.objects.values_list("focus_axes", flat=True).distinct()
            )
        )

        data = {
            "level": [
                {"value": c.value, "label": c.label}
                for c in Level
                if c.value in used_levels
            ],
            "focus": [
                {"value": c.value, "label": c.label}
                for c in Focus
                if c.value in used_focuses
            ],
            "focus_axes": [
                {"value": c.value, "label": c.label}
                for c in FocusAxis
                if c.value in used_focus_axes
            ],
        }
        serializer = ProgramFiltersSerializer(data=data)
        serializer.is_valid()
        return Response(serializer.data)


###################################################################################################
# EXERCISE
###################################################################################################
class ExerciseViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.IsAdminUser]
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer


###################################################################################################
# EXERCISE FILTERS
###################################################################################################
@extend_schema(responses=ExerciseFiltersSerializer)
class ExerciseFiltersView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        used_resolutions = Exercise.objects.values_list(
            "resolution", flat=True
        ).distinct()
        used_practice_zones = Exercise.objects.values_list(
            "practice_zone", flat=True
        ).distinct()

        data = {
            "resolution": [
                {"value": c.value, "label": c.label}
                for c in Resolution
                if c.value in used_resolutions
            ],
            "practice_zone": [
                {"value": c.value, "label": c.label}
                for c in PracticeZone
                if c.value in used_practice_zones
            ],
        }
        serializer = ExerciseFiltersSerializer(data)
        return Response(serializer.data)
