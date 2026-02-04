from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied


class CurrentUserOnlyMixin(viewsets.GenericViewSet):
    """
    Mixin DRF so the user only sees their own objects,
    + automatically filters on user_program_id if present in the URL.
    """

    user_field: str = "user_id"

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.filter(**{self.user_field: self.request.user.id})

        user_program_id = self.kwargs.get("user_program_id")
        if user_program_id:
            qs = qs.filter(user_program_id=user_program_id)

            if not qs.exists():
                raise PermissionDenied("You are not allowed to access this resource.")

        return qs

    def get_permissions(self):
        return [permissions.IsAuthenticated()]
