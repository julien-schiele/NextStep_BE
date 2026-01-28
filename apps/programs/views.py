from rest_framework import viewsets, permissions
from .models import Program, Exercise
from .serializers import ProgramSerializer, ExerciseSerializer


class AuthenticatedReadAdminWriteViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet:
    - Authenticated users can GET (list/retrieve)
    - Only admin users can POST, PUT, PATCH, DELETE
    """

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]


class ProgramViewSet(AuthenticatedReadAdminWriteViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer


class ExerciseViewSet(AuthenticatedReadAdminWriteViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
