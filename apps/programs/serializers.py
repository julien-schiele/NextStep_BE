from rest_framework import serializers
from .models import Exercise, Program
from .services.program_services import ProgramService


# -------------------------------
# Exercise Serializer
# -------------------------------
class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = [
            "slug",
            "name",
            "description",
            "resolution",
            "practice_zone",
            "image",
            "gif",
            "video",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]


# -------------------------------
# Session Serializer
# -------------------------------
class SessionSerializer(serializers.Serializer):
    session = serializers.IntegerField()
    sequences = serializers.ListField(
        child=serializers.ListSerializer(child=ExerciseSerializer())
    )


# -------------------------------
# Cycle Serializer
# -------------------------------
class CycleSerializer(serializers.Serializer):
    cycle = serializers.IntegerField()
    sessions = SessionSerializer(many=True)


# -------------------------------
# Program Content Serializer
# -------------------------------
class ProgramContentSerializer(serializers.Serializer):
    cycles = CycleSerializer(many=True)


# -------------------------------
# Program List Serializer
# -------------------------------
class ProgramListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = [
            "id",
            "name",
            "description",
            "level",
            "focus",
            "duration_days",
        ]


# -------------------------------
# Program Create Serializer
# -------------------------------
class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "realistic_if",
            "not_realistic_if",
            "focus",
            "level",
            "duration_days",
            "is_public",
            "content",
            "focus_axes",
            "cycle_rhythm",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


# -------------------------------
# Program Detail Serializer
# -------------------------------
class ProgramDetailSerializer(serializers.ModelSerializer):
    content = ProgramContentSerializer()

    class Meta:
        model = Program
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "realistic_if",
            "not_realistic_if",
            "focus",
            "level",
            "duration_days",
            "focus_axes",
            "is_public",
            "content",
            "cycle_rhythm",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def to_representation(self, obj):
        data = super().to_representation(obj)
        program_services = ProgramService(obj)
        data["content"] = program_services.compute_preview()
        return data
