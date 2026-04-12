from django.urls import path
from .views import (
    ChangePasswordView,
    CookieRefreshView,
    CookieTokenView,
    CurrentUserView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetView,
    UserListView,
    UserDetailView,
    UserCreateView,
)

urlpatterns = [
    # JWT auth
    path("token/", CookieTokenView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CookieRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # Reset password
    path(
        "request-password-reset/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "reset-password/",
        PasswordResetView.as_view(),
        name="password-reset",
    ),
    # Update password
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    # User CRUD
    # TODO: The 2 below are not useful from a UX perspective, and may raises GDPR/security questions.
    # path("users/", UserListView.as_view(), name="user-list"),
    # path("users/<uuid:id>/", UserDetailView.as_view(), name="user-detail"),
    path("users/create/", UserCreateView.as_view(), name="user-create"),
    # Others
    path("users/current/", CurrentUserView.as_view(), name="current-user"),
]
