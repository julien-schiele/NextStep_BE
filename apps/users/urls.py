from django.urls import path
from .views import CurrentUserView, UserListView, UserDetailView, UserCreateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # JWT auth
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # User CRUD
    path("users/", UserListView.as_view(), name="user-list"),
    path('api/users/<uuid:id>/', UserDetailView.as_view(), name='user-detail'),
    path("users/create/", UserCreateView.as_view(), name="user-create"),
    
    # Others
    path("users/me/", CurrentUserView.as_view(), name="current-user"),
]
