from rest_framework import serializers
from .models import Exercise, Program
from .services.program_services import ProgramService
from drf_spectacular.utils import extend_schema_field


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
# Exercise in computed sequence Serializer
# -------------------------------
class ExercisePreviewSerializer(serializers.Serializer):
    slug = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    resolution = serializers.CharField()
    practice_zone = serializers.CharField()
    value = serializers.IntegerField()


# -------------------------------
# Session Serializer
# -------------------------------
class SessionSerializer(serializers.Serializer):
    session = serializers.IntegerField()
    sequences = serializers.ListField(
        child=serializers.ListSerializer(
            child=ExercisePreviewSerializer()
        )
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
class ProgramDetailContentSerializer(serializers.Serializer):
    cycles = CycleSerializer(many=True)
    total_cycles = serializers.IntegerField()
    sessions_per_cycles = serializers.IntegerField()
    total_sessions = serializers.IntegerField()


# -------------------------------
# Program Detail Serializer
# -------------------------------
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
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    @extend_schema_field(ProgramDetailContentSerializer)
    def get_content(self, obj):
        program_services = ProgramService(obj)
        raw_content = program_services.compute_preview()
        serializer = ProgramDetailContentSerializer(instance=raw_content)
        return serializer.data
    

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
# Filter Option Serializer
# -------------------------------
class FilterOptionSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


# -------------------------------
# Program Filters Serializer
# -------------------------------
class ProgramFiltersSerializer(serializers.Serializer):
    level = FilterOptionSerializer(many=True)
    focus = FilterOptionSerializer(many=True)
    focus_axes = FilterOptionSerializer(many=True)