from apps.users.services import (
    generate_reset_token,
    reset_password_with_token,
    send_reset_password_email,
)
from django.shortcuts import get_object_or_404
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
from .models import User
from rest_framework import status
from drf_spectacular.utils import OpenApiResponse, extend_schema


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


class CurrentUserView(APIView):
    """
    Retrieve the current authenticated user
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class CookieTokenView(TokenObtainPairView):

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=TokenResponseSerializer,
                description="JWT tokens + HttpOnly refresh_token cookie",
            )
        }
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        refresh_token = response.data.get("refresh")

        client_type = request.headers.get("X-Client-Type", "web")

        # Mobile do not rely on cookie...
        if client_type != "mobile":
            del response.data["refresh"]

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="Lax",
        )

        return response


class CookieRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        request.data["refresh"] = request.COOKIES.get("refresh_token")
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """
    Delete refresh token cookie
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({"detail": "Logged out"})
        response.delete_cookie("refresh_token")
        return response


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

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
    permission_classes = [IsAuthenticated]

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
            raise ValidationError({"detail": "Current password is incorrect."})

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )
