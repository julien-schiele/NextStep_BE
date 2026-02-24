from apps.programs.choices import Focus, FocusAxis, Level
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
    realistic_if = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    not_realistic_if = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )

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
            "level",
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
    realistic_if = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    not_realistic_if = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    
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
# Program Filters Serializer
# -------------------------------

class LevelFilterSerializer(serializers.Serializer):
    value = serializers.ChoiceField(choices=Level.choices)
    label = serializers.CharField()
    
class FocusFilterSerializer(serializers.Serializer):
    value = serializers.ChoiceField(choices=Focus.choices)
    label = serializers.CharField()
    
class FocusAxesFilterSerializer(serializers.Serializer):
    value = serializers.ChoiceField(choices=FocusAxis.choices)
    label = serializers.CharField()
    
class ProgramFiltersSerializer(serializers.Serializer):
    level = LevelFilterSerializer(many=True)
    focus = FocusFilterSerializer(many=True)
    focus_axes = FocusAxesFilterSerializer(many=True)