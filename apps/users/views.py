from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import UserSerializer, UserCreateSerializer
from .models import User


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
        response.delete_cookie("refresh")
        return response
