"""
apps/users/permissions.py
==========================
DRF permission to block write actions on demo accounts.

Usage
-----
    from apps.users.permissions import IsNotDemoUser

    class ChangePasswordView(APIView):
        permission_classes = [IsAuthenticated, IsNotDemoUser]

Endpoints to protect (see schema.yaml)
---------------------------------------
    POST   /api/change-password/                         ← change password
    POST   /api/request-password-reset/                  ← trigger a reset email
    POST   /api/reset-password/                          ← reset via token
    DELETE /api/user-programs/{user_program_id}/sessions/{id}  ← delete a session

Intentionally NOT blocked
--------------------------
    POST   /api/users/create/          → allowing visitors to create a real account is useful
    GET    /api/users/me/              → read-only, fine
    POST   /api/user-programs/        → demo can "test" enrollment (daily reset anyway)
    PATCH  /api/user-programs/{id}/   → same, daily reset
    POST   /api/user-programs/{id}/sessions/    → same
    POST   /api/user-programs/{id}/feedbacks/   → same

    Note: exercises PUT/PATCH/DELETE and programs PUT/PATCH/DELETE are already
    protected by is_staff / is_admin in the views — no need to touch them.
"""

from rest_framework.permissions import BasePermission

DEMO_EMAILS: frozenset[str] = frozenset(
    {
        "demo1@nextstep.com",
        "demo2@nextstep.com",
        "demo3@nextstep.com",
    }
)


class IsNotDemoUser(BasePermission):
    """
    Denies access to demo users on sensitive endpoints.
    Returns HTTP 403 with an explicit message — the frontend can display
    a toast like "This action is disabled in demo mode".
    """

    message = "This action is disabled for demo accounts."

    def has_permission(self, request, view) -> bool:
        if request.user and request.user.is_authenticated:
            return request.user.email not in DEMO_EMAILS
        # Unauthenticated requests → let through (IsAuthenticated will handle it)
        return True