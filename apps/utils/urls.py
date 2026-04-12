from django.urls import path
from .views import PrivacyPolicyView

urlpatterns = [
    path("privacy/", PrivacyPolicyView.as_view(), name="privacy_policy"),
]
