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
from .models import UserProgram, UserProgramSession, UserProgramFeedback
from .mixins import CurrentUserOnlyMixin


class UserProgramViewSet(CurrentUserOnlyMixin, viewsets.ModelViewSet):
    """
    Only:
    - GET /user-programs/{id}/feedbacks/
    - POST /user-programs/{id}/feedbacks/
    """

    queryset = UserProgram.objects.all()
    serializer_class = UserProgramSerializer
    user_field = "user_id"
    http_method_names = ["get", "patch", "post", "head", "options"]


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
    - PATCH /user-programs/{user_program_id}/sessions/{id}/
    - DELETE /user-programs/{user_program_id}/sessions/{id}/
    """

    serializer_class = UserProgramSessionSerializer
    queryset = UserProgramSession.objects.all()
    user_field = "user_program__user_id"
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    lookup_field = "id"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user_program_id=self.kwargs["user_program_id"])
    
    def get_serializer_class(self):
        if self.action == "partial_update":
            return UserProgramSessionPatchSerializer
        return super().get_serializer_class()
    
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        session = self.get_object()
        user_program = session.user_program
        service = UserProgramService(user_program)
        service.update_program_status_if_needed()
        return response
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.completed == True:
            return Response(
                {"detail": "This session is complete and cannot be deleted."},
                status=status.HTTP_403_FORBIDDEN
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
    """

    serializer_class = UserProgramFeedbackSerializer
    queryset = UserProgramFeedback.objects.all()
    user_field = "user_program__user_id"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user_program_id=self.kwargs["user_program_id"])
