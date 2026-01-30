from django import forms
from django.contrib import admin
from django.utils.text import slugify
from parler.admin import TranslatableAdmin
from apps.programs.models import Exercise, Program


@admin.register(Exercise)
class ExerciseAdmin(TranslatableAdmin):

    list_display = ("name", "resolution", "slug")
    list_filter = ("resolution",)
    search_fields = ("translations__name",)

    fieldsets = (
        (None, {"fields": ("slug", "resolution")}),
        (
            "Media",
            {
                "fields": ("image", "gif", "video"),
            },
        ),
        (
            "Details",
            {
                "fields": ("name", "description"),
            },
        ),
    )

    readonly_fields = ("slug",)


@admin.register(Program)
class ProgramAdmin(TranslatableAdmin):
    list_display = ("name", "focus", "level", "duration_days", "is_public")
    list_filter = ("focus", "level", "is_public")
    search_fields = ("translations__name",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "slug",
                    "name",
                    "description",
                    "realistic_if",
                    "not_realistic_if"
                )
            },
        ),
        (
            "Program Details",
            {
                "fields": (
                    "focus",
                    "level",
                    "is_public",
                    "focus_axes",
                    "cycle_rhythm",
                    "duration_days",
                    "content",
                ),
            },
        ),
    )

    readonly_fields = ("slug", "duration_days")