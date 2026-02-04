from apps.tracking.choices import Rating, Status, Usefunlness
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import UserProgram, UserProgramSession, UserProgramFeedback
from apps.tracking.services import UserProgramService


class UserProgramSerializer(serializers.ModelSerializer):
    next_cycle = serializers.SerializerMethodField()
    next_session_in_cycle = serializers.SerializerMethodField()

    class Meta:
        model = UserProgram
        fields = [
            "id",
            "user",
            "program",
            "status",
            "created_at",
            "updated_at",
            "next_cycle",
            "next_session_in_cycle",
        ]
        read_only_fields = [
            "user",
            "created_at",
            "updated_at",
            "next_cycle",
            "next_session_in_cycle",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        validated_data["status"] = Status.ACTIVE
        return super().create(validated_data)

    def get_next_cycle(self, obj):
        service = UserProgramService(obj)
        return service.next_step_in_program()["cycle"]

    def get_next_session_in_cycle(self, obj):
        service = UserProgramService(obj)
        return service.next_step_in_program()["session"]


class UserProgramSessionSerializer(serializers.ModelSerializer):
    completed = serializers.ReadOnlyField()

    class Meta:
        model = UserProgramSession
        fields = [
            "id",
            "user_program",
            "session_in_cycle",
            "cycle_count",
            "completed",
            "session_snapshot",
            "rating",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user_program", "created_at", "updated_at"]

    def create(self, validated_data):
        user_program_id = self.context["view"].kwargs.get("user_program_id")
        user_program = get_object_or_404(
            UserProgram,
            id=user_program_id,
            user=self.context["request"].user,
        )

        session, created = UserProgramSession.objects.get_or_create(
            user_program=user_program,
            cycle_count=validated_data["cycle_count"],
            session_in_cycle=validated_data["session_in_cycle"],
            defaults=validated_data,
        )

        return session


class UserProgramSessionPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgramSession
        fields = [
            "id",
            "user_program",
            "session_in_cycle",
            "cycle_count",
            "completed",
            "session_snapshot",
            "rating",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user_program",
            "session_in_cycle",
            "cycle_count",
            "completed",
            "session_snapshot",
            "created_at",
            "updated_at",
        ]

    def update(self, instance, validated_data):
        instance.rating = validated_data.get("rating", instance.rating)
        instance.save()
        return instance


class UserProgramFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgramFeedback
        fields = [
            "id",
            "user_program",
            "usefulness",
            "would_repeat",
            "comment",
        ]
        read_only_fields = [
            "id",
            "user_program",
        ]

    def validate(self, attrs):
        if not any(
            [attrs.get("usefulness"), attrs.get("would_repeat"), attrs.get("comment")]
        ):
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "At least one of the fields 'usefulness', 'would_repeat', or 'comment' must be provided."
                    ]
                }
            )
        return attrs

    def create(self, validated_data):
        user_program = UserProgram.objects.get(
            id=self.context["view"].kwargs["user_program_id"]
        )
        validated_data["user_program"] = user_program
        return super().create(validated_data)
