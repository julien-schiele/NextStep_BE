import json
from django.db import transaction
from apps.programs.models import Exercise
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create Exercise model entries from JSON fixture (atomic)"

    def add_arguments(self, parser):
        parser.add_argument(
            "fixture_file", type=str, help="Path to the JSON fixture file"
        )

    def create(self, data):
        for idx, item in enumerate(data, start=1):
            translations = item.get("translations", {})
            if not translations:
                raise ValueError(f"ITEM #{idx} has no translations")

            exercise = Exercise.objects.create(
                practice_zone=item.get("practice_zone"),
                resolution=item.get("resolution"),
                image=item.get("image"),
                gif=item.get("gif"),
                video=item.get("video"),
            )

            for lang_code, trans in translations.items():
                exercise.set_current_language(lang_code)
                exercise.name = trans.get("name", "")
                exercise.description = trans.get("description", "")
                exercise.save()

    def handle(self, *args, **options):
        fixture_file = options["fixture_file"]

        try:
            with open(fixture_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            with transaction.atomic():
                Exercise.objects.all().delete()
                self.create(data)

            self.stdout.write(
                self.style.SUCCESS(
                    "✅ Successfully loaded ALL Exercise entries (atomic)."
                )
            )

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"❌ Import failed, nothing was saved: {e}")
            )
