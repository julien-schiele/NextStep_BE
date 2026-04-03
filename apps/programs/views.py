from rest_framework import viewsets, permissions, views
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


###################################################################################################
# PROGRAM
###################################################################################################
class ProgramViewSet(viewsets.ModelViewSet):
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
        if self.action in ("retrieve"):
            return ProgramDetailSerializer
        return ProgramSerializer


###################################################################################################
# PROGRAM FILTERS
###################################################################################################
class ProgramFiltersView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses=ProgramFiltersSerializer)
    def get(self, request, *args, **kwargs):
        data = {
            "level": [{"value": c.value, "label": c.label} for c in Level],
            "focus": [{"value": c.value, "label": c.label} for c in Focus],
            "focus_axes": [{"value": c.value, "label": c.label} for c in FocusAxis],
        }
        serializer = ProgramFiltersSerializer(data=data)
        serializer.is_valid()
        return Response(serializer.data)


###################################################################################################
# EXERCISE
###################################################################################################
class ExerciseViewSet(viewsets.ModelViewSet):
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
        data = {
            "resolution": [{"value": c.value, "label": c.label} for c in Resolution],
            "practice_zone": [
                {"value": c.value, "label": c.label} for c in PracticeZone
            ],
        }
        serializer = ExerciseFiltersSerializer(data)
        return Response(serializer.data)
