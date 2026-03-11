from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "date_joined",
        ]
        read_only_fields = ["id", "is_staff", "date_joined"]


class UserCreateSerializer(serializers.ModelSerializer):
    gdpr_consent = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password", "gdpr_consent"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data["gdpr_consent_date"] = timezone.now()
        user = User.objects.create_user(password=password, **validated_data)
        return user

    def to_internal_value(self, data):
        result = super().to_internal_value(data)
        if not result.get("gdpr_consent", False):
            raise ValidationError({"error": _("You must accept the privacy policy.")})
        return result


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetRequestResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, min_length=8)


class PasswordResetResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class PasswordResetErrorResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class ChangePasswordResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class ChangePasswordErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField(required=False)
