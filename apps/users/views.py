from apps.users.services import (
    generate_reset_token,
    reset_password_with_token,
    send_reset_password_email,
)
from django.shortcuts import get_object_or_404
from apps.users.permissions import IsNotDemoUser
from apps.utils.permissions import IsAuthenticatedExcludeOptions
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import (
    ChangePasswordErrorSerializer,
    ChangePasswordResponseSerializer,
    ChangePasswordSerializer,
    PasswordResetErrorResponseSerializer,
    PasswordResetRequestResponseSerializer,
    PasswordResetRequestSerializer,
    PasswordResetResponseSerializer,
    PasswordResetSerializer,
    TokenResponseSerializer,
    UserSerializer,
    UserCreateSerializer,
)
from django.conf import settings
from .models import User
from rest_framework import status
from drf_spectacular.utils import OpenApiResponse, extend_schema
from django.utils.translation import gettext_lazy as _


class UserListView(generics.ListAPIView):
    """
    List all users (admin only)
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single user by UUID (admin only)
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = "id"
    lookup_url_kwarg = "id"


class UserCreateView(generics.CreateAPIView):
    """
    Create a new user (public)
    """

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(responses=UserSerializer)
class CurrentUserView(APIView):
    """
    Retrieve the current authenticated user
    """

    permission_classes = [IsAuthenticatedExcludeOptions]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(request=None, responses={204: None})
    def delete(self, request):
        permission = IsNotDemoUser()
        if not permission.has_permission(request, self):
            return Response(
                {"detail": permission.message}, status=status.HTTP_403_FORBIDDEN
            )
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CookieTokenView(TokenObtainPairView):

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=TokenResponseSerializer,
                description="JWT tokens + HttpOnly refresh token cookie",
            )
        }
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        access_token = response.data.get("access")
        refresh_token = response.data.get("refresh")

        client_type = request.headers.get("X-Client-Type", "web")

        # Mobile do not rely on cookie...
        if client_type != "mobile":
            response.set_cookie(
                key="_at",
                value=access_token,
                secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", False),
                httponly=False,  # accessible SSR
                samesite=settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
            )

            response.set_cookie(
                key="_rt",
                value=refresh_token,
                secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", False),
                httponly=True,  # secure
                samesite=settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
            )
            response.data.pop("refresh", None)

        return response


class CookieRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("_rt")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        request.data["refresh"] = refresh_token

        response = super().post(request, *args, **kwargs)

        new_access = response.data.get("access")
        new_refresh = response.data.get("refresh")

        if new_access:
            response.set_cookie(
                key="_at",
                value=new_access,
                secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", False),
                httponly=False,
                samesite=settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
            )

        if new_refresh:
            response.set_cookie(
                key="_rt",
                value=new_refresh,
                secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", False),
                httponly=True,
                samesite=settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
            )

        return response


@extend_schema(
    request=None,
    responses={200: {"type": "object", "properties": {"detail": {"type": "string"}}}},
)
class LogoutView(APIView):
    """
    Delete refresh token cookie
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"detail": "Logged out"})
        response.delete_cookie("_at")
        response.delete_cookie("_rt")
        return response


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny, IsNotDemoUser]

    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={200: PasswordResetRequestResponseSerializer},
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = get_object_or_404(User, email=email)

        token = generate_reset_token(user)
        send_reset_password_email(email, token)

        return Response(
            {"message": "Password reset email sent successfully."},
            status=status.HTTP_200_OK,
        )


class PasswordResetView(APIView):
    permission_classes = [AllowAny, IsNotDemoUser]

    @extend_schema(
        request=PasswordResetSerializer,
        responses={
            200: PasswordResetResponseSerializer,
            400: PasswordResetErrorResponseSerializer,
        },
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        reset_password_with_token(token, new_password)

        return Response(
            {"message": "Password reset successfully."},
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated, IsNotDemoUser]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: ChangePasswordResponseSerializer,
            400: ChangePasswordErrorSerializer,
            401: ChangePasswordErrorSerializer,
        },
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):
            raise ValidationError(_("Current password is incorrect."))

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )
