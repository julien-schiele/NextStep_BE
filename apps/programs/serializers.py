from rest_framework import serializers
from .models import Exercise, Program
from .services.program_services import ProgramService


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
        
class ProgramDetailSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = [
            "id",
            "name",
            "description",
            "realistic_if",
            "not_realistic_if",
            "focus",
            "level",
            "duration_days",
            "focus_axes",
            "content",
        ]

    def get_content(self, obj):
        program_services = ProgramService(obj)
        return program_services.compute_preview()
