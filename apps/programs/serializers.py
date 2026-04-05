from apps.programs.choices import Focus, FocusAxis, Level, PracticeZone, Resolution
from rest_framework import serializers
from .models import Exercise, Program
from .services.program_services import ProgramService
from drf_spectacular.utils import extend_schema_field


# -------------------------------
# Exercise Serializer
# -------------------------------
class ExerciseSerializer(serializers.ModelSerializer):
    translations = serializers.DictField(
        child=serializers.DictField(child=serializers.CharField()),
        write_only=True,
        required=True,
    )
    name = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Exercise
        fields = [
            "slug",
            "name",
            "description",
            "translations",
            "resolution",
            "practice_zone",
            "image",
            "gif",
            "video",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]

    def get_name(self, obj):
        return obj.safe_translation_getter("name", any_language=True)

    def get_description(self, obj):
        return obj.safe_translation_getter("description", any_language=True)

    def create(self, validated_data):
        translations = validated_data.pop("translations", {})
        instance = super().create(validated_data)
        for lang_code, fields in translations.items():
            instance.set_current_language(lang_code)
            for field_name, value in fields.items():
                setattr(instance, field_name, value)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        translations = validated_data.pop("translations", {})
        instance = super().update(instance, validated_data)
        for lang_code, fields in translations.items():
            instance.set_current_language(lang_code)
            for field_name, value in fields.items():
                setattr(instance, field_name, value)
        instance.save()
        return instance


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
        child=serializers.ListSerializer(child=ExercisePreviewSerializer())
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
    name = serializers.CharField(help_text="Translated field (django-parler)")
    description = serializers.CharField(help_text="Translated field (django-parler)")
    content = serializers.SerializerMethodField()
    realistic_if = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )
    not_realistic_if = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
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
    name = serializers.CharField(help_text="Translated field (django-parler)")
    description = serializers.CharField(help_text="Translated field (django-parler)")

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
    name = serializers.CharField(help_text="Translated field (django-parler)")
    description = serializers.CharField(
        required=False, allow_blank=True, help_text="Translated field (django-parler)"
    )
    realistic_if = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )
    not_realistic_if = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
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


class ResolutionFilterSerializer(serializers.Serializer):
    value = serializers.ChoiceField(choices=Resolution.choices)
    label = serializers.CharField()


class PracticeZoneFilterSerializer(serializers.Serializer):
    value = serializers.ChoiceField(choices=PracticeZone.choices)
    label = serializers.CharField()


class ExerciseFiltersSerializer(serializers.Serializer):
    resolution = ResolutionFilterSerializer(many=True)
    practice_zone = PracticeZoneFilterSerializer(many=True)
