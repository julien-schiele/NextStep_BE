from rest_framework.routers import DefaultRouter
from django.urls import path
from apps.tracking.views import (
    UserProgramViewSet,
    UserProgramSessionViewSet,
    UserProgramFeedbackViewSet,
    UserStatsView,
)

router = DefaultRouter()
router.register(r"user-programs", UserProgramViewSet, basename="user-program")

urlpatterns = [
    # Stats
    path("user-stats/", UserStatsView.as_view(), name="user-stats"),
    # Sessions
    path(
        "user-programs/<uuid:user_program_id>/sessions/",
        UserProgramSessionViewSet.as_view({"get": "list", "post": "create"}),
        name="user-program-sessions",
    ),
    path(
        "user-programs/<uuid:user_program_id>/sessions/<uuid:id>",
        UserProgramSessionViewSet.as_view(
            {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
        ),
        name="user-program-session-detail",
    ),
    # Feedbacks
    path(
        "user-programs/<uuid:user_program_id>/feedbacks/",
        UserProgramFeedbackViewSet.as_view({"get": "list", "post": "create"}),
        name="user-program-feedbacks",
    ),
    path(
        "user-programs/<uuid:user_program_id>/feedbacks/<uuid:id>",
        UserProgramFeedbackViewSet.as_view(
            {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
        ),
        name="user-program-feedback-detail",
    ),
]


urlpatterns += router.urls
