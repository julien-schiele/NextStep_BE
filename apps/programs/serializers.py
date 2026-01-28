from rest_framework import serializers
from .models import Exercise, Program


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "practice_zone",
            "image",
            "gif",
            "video",
            "resolution",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


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
