from apps.programs.choices import Level
from apps.tracking.choices import Status
from apps.tracking.filters import UserProgramFilter
from rest_framework.response import Response
from rest_framework import status
from apps.tracking.services import UserProgramService
from rest_framework import viewsets, mixins
from apps.tracking.serializers import (
    UserProgramSerializer,
    UserProgramSessionPatchSerializer,
    UserProgramSessionSerializer,
    UserProgramFeedbackSerializer,
)
from .models import UserProgram, UserProgramSession, UserProgramFeedback, Status
from .mixins import CurrentUserOnlyMixin
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.views import APIView
from .serializers import UserStatsSerializer
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

class UserProgramViewSet(CurrentUserOnlyMixin, viewsets.ModelViewSet):
    """
    Only:
    - GET /user-programs/
    - POST /user-programs/
    - GET /user-programs/{id}/
    - PATCH /user-programs/{id}/
    """

    filter_backends = [DjangoFilterBackend]
    filterset_class = UserProgramFilter
    queryset = UserProgram.objects.all()
    serializer_class = UserProgramSerializer
    user_field = "user_id"
    http_method_names = ["get", "patch", "post", "head", "options"]

    def get_queryset(self):
        return (
            UserProgram.objects.select_related("program")
            .prefetch_related("sessions")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        user = self.request.user
        if UserProgram.objects.filter(user=user, status=Status.ACTIVE).exists():
            raise ValidationError("User already has an active program.")
        serializer.save(user=user, status=Status.ACTIVE)

    @action(detail=False, methods=["get"], url_path="active")
    def active(self, request):
        """
        GET /user-programs/active/
        Return active instance for current user, or null if none.
        """
        active_program = UserProgram.objects.filter(
            user=request.user, status=Status.ACTIVE
        ).first()

        serializer = self.get_serializer(active_program)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProgramSessionViewSet(
    CurrentUserOnlyMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Only:
    - GET /user-programs/{id}/sessions/
    - POST /user-programs/{id}/sessions/
    - GET /user-programs/{user_program_id}/sessions/{id}/
    - DELETE /user-programs/{user_program_id}/sessions/{id}/
    """

    serializer_class = UserProgramSessionSerializer
    queryset = UserProgramSession.objects.all()
    user_field = "user_program__user_id"
    http_method_names = ["get", "post", "delete", "head", "options"]
    lookup_field = "id"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user_program_id=self.kwargs["user_program_id"])

    def get_serializer_class(self):
        if self.action == "partial_update":
            return UserProgramSessionPatchSerializer
        return super().get_serializer_class()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.completed == True:
            return Response(
                {"detail": "This session is complete and cannot be deleted."},
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProgramFeedbackViewSet(
    CurrentUserOnlyMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Only:
    - GET /user-programs/{id}/feedback/
    - POST /user-programs/{id}/feedback/
    - GET /user-programs/{id}/feedback/{id}/
    """

    serializer_class = UserProgramFeedbackSerializer
    queryset = UserProgramFeedback.objects.all()
    user_field = "user_program__user_id"
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user_program_id=self.kwargs["user_program_id"])


class UserStatsView(APIView):
    permission_classes = [IsAuthenticated]

    LEVEL_WEIGHTS = {
        Level.BEGINNER: 1,
        Level.INTERMEDIATE: 2,
        Level.ADVANCED: 3,
    }

    @extend_schema(responses=UserStatsSerializer)
    def get(self, request):
        user = request.user

        # Total completed sessions
        total_sessions = UserProgramSession.objects.filter(
            user_program__user=user,
            rating__isnull=False,
        ).count()

        # Completed programs
        completed_programs = UserProgram.objects.filter(
            user=user, status=Status.COMPLETED
        ).select_related("program")

        total_programs_completed = completed_programs.count()

        # Highest level completed
        highest_level_completed = None

        if completed_programs.exists():
            max_weight = max(
                self.LEVEL_WEIGHTS[up.program.level] for up in completed_programs
            )

            # reverse lookup
            reverse_map = {v: k for k, v in self.LEVEL_WEIGHTS.items()}
            highest_level_completed = reverse_map[max_weight]

        # Current level (active program if exists, else highest completed)
        active_program = (
            UserProgram.objects.filter(user=user, status=Status.ACTIVE)
            .select_related("program")
            .first()
        )

        current_level = (
            active_program.program.level if active_program else highest_level_completed
        )
        
        # Get translated labels
        current_level_label = Level(current_level).label
        highest_level_completed_label = Level(highest_level_completed).label

        data = {
            "total_sessions_completed": total_sessions,
            "total_programs_completed": total_programs_completed,
            "current_level": current_level_label,
            "highest_level_completed": highest_level_completed_label,
        }

        serializer = UserStatsSerializer(data)
        return Response(serializer.data)
