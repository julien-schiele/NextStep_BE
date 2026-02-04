from rest_framework import viewsets, permissions, views
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .choices import Focus, Level, FocusAxis, PracticeZone, Resolution
from .models import Program, Exercise
from .serializers import (
    ProgramListSerializer,
    ProgramDetailSerializer,
    ExerciseSerializer,
    ProgramSerializer,
)
from .filters import ProgramFilter


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

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "level": [{"value": c.value, "label": c.label} for c in Level],
                "focus": [{"value": c.value, "label": c.label} for c in Focus],
                "focus_axes": [{"value": c.value, "label": c.label} for c in FocusAxis],
            }
        )


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
class ExerciseFiltersView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "resolution": [
                    {"value": c.value, "label": c.label} for c in Resolution
                ],
                "practice_zone": [
                    {"value": c.value, "label": c.label} for c in PracticeZone
                ],
            }
        )
