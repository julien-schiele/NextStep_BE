from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import PrivacyPolicy


class PrivacyPolicyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        policy = PrivacyPolicy.objects.last()
        if not policy:
            return Response({"detail": "Privacy policy not set"}, status=404)

        return Response(
            {
                "short_text": policy.safe_translation_getter("short_text"),
                "long_text": policy.safe_translation_getter("long_text"),
            }
        )
