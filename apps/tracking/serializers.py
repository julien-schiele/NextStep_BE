from apps.programs.choices import Level
from apps.tracking.choices import Rating, Status, Usefunlness
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import UserProgram, UserProgramSession, UserProgramFeedback
from apps.tracking.services import UserProgramService
from drf_spectacular.utils import extend_schema_field


class UserProgramSerializer(serializers.ModelSerializer):
    next_cycle = serializers.SerializerMethodField()
    next_session_in_cycle = serializers.SerializerMethodField()
    program_name = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)

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
            "program_name",
            "start_date",
            "end_date",
            "status_display",
        ]
        read_only_fields = [
            "user",
            "created_at",
            "updated_at",
            "next_cycle",
            "next_session_in_cycle",
            "program_name",
            "start_date",
            "end_date",
            "status_display",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        validated_data["status"] = Status.ACTIVE
        return super().create(validated_data)

    @extend_schema_field(serializers.IntegerField)
    def get_next_cycle(self, obj):
        service = UserProgramService(obj)
        return service.next_step_in_program()["cycle"]

    @extend_schema_field(serializers.IntegerField)
    def get_next_session_in_cycle(self, obj):
        service = UserProgramService(obj)
        return service.next_step_in_program()["session"]

    @extend_schema_field(serializers.CharField)
    def get_program_name(self, obj):
        return obj.program.name

    @extend_schema_field(serializers.DateTimeField)
    def get_start_date(self, obj):
        first_session = obj.sessions.order_by("created_at").first()
        return first_session.created_at if first_session else None

    @extend_schema_field(serializers.DateTimeField)
    def get_end_date(self, obj):
        if obj.status == Status.ACTIVE:
            return None
        last_session = obj.sessions.order_by("-created_at").first()
        return last_session.created_at if last_session else None


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

        service = UserProgramService(user_program)
        service.update_program_status_if_needed()

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


class UserStatsSerializer(serializers.Serializer):
    total_sessions_completed = serializers.IntegerField()
    total_programs_completed = serializers.IntegerField()
    current_level = serializers.ChoiceField(
        choices=Level.choices, allow_null=True, allow_blank=True
    )
    highest_level_completed = serializers.ChoiceField(
        choices=Level.choices, allow_null=True, allow_blank=True
    )
