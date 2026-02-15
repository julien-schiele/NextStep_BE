from apps.utils.serializers import PrivacyPolicySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import PrivacyPolicy
from drf_spectacular.utils import extend_schema


class PrivacyPolicyView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses=PrivacyPolicySerializer)
    def get(self, request):
        policy = PrivacyPolicy.objects.last()

        if not policy:
            return Response({"detail": "Privacy policy not set"}, status=404)

        serializer = PrivacyPolicySerializer(policy)
        return Response(serializer.data)
