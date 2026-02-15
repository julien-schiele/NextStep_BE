from rest_framework import serializers
from .models import PrivacyPolicy


class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = [
            "short_text",
            "long_text",
        ]
        read_only_fields = ["short_text", "long_text"]
