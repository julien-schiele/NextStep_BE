from rest_framework import serializers
from .models import PrivacyPolicy


class PrivacyPolicySerializer(serializers.ModelSerializer):
    short_text = serializers.CharField(help_text="Translated field (django-parler)")
    long_text = serializers.CharField(help_text="Translated field (django-parler)")

    class Meta:
        model = PrivacyPolicy
        fields = [
            "short_text",
            "long_text",
        ]
        read_only_fields = ["short_text", "long_text"]
