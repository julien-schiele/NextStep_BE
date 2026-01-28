from rest_framework import serializers
from .models import Exercise, Program


class ExerciseSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = [
            "id",
            "slug",
            "translations",
            "practice_zone",
            "image",
            "gif",
            "video",
            "resolution",  # 'repeat' ou 'duration'
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_translations(self, obj):
        """
        Return all translations as a simple dict:
        { "en": {"name": ..., "description": ...}, "fr": {...} }
        """
        data = {}
        for lang_code, _ in obj.get_available_languages():
            obj.set_current_language(lang_code)
            data[lang_code] = {
                "name": obj.name,
                "description": obj.description,
            }
        return data


class ProgramSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()
    class Meta:
        model = Program
        fields = [
            "id",
            "slug",
            "translations",
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

    def get_translations(self, obj):
        """
        Return all translations as a simple dict:
        { "en": {"name": ..., "description": ...}, "fr": {...} }
        """
        data = {}
        for lang_code, _ in obj.get_available_languages():
            obj.set_current_language(lang_code)
            data[lang_code] = {
                "name": obj.name,
                "description": obj.description,
                "realistic_if": obj.realistic_if,
                "not_realistic_ifn": obj.not_realistic_if,
            }
        return data