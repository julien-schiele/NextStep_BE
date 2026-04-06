import json
from django.db import transaction
from django.utils.text import slugify
from apps.programs.models import Exercise
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update Exercise model entries from JSON fixture (atomic)"

    def add_arguments(self, parser):
        parser.add_argument(
            "fixture_file", type=str, help="Path to the JSON fixture file"
        )

    def get_slug_from_item(self, item):
        """Generate slug from the English translation name, matching model's save() logic."""
        en_name = item.get("translations", {}).get("en", {}).get("name", "")
        if en_name and en_name.strip():
            return slugify(en_name).replace("-", "_")
        return None

    def upsert(self, data):
        created_count = 0
        updated_count = 0

        for idx, item in enumerate(data, start=1):
            translations = item.get("translations", {})
            if not translations:
                raise ValueError(f"ITEM #{idx} has no translations")

            slug = self.get_slug_from_item(item)
            if not slug:
                raise ValueError(f"ITEM #{idx} has no valid name to generate a slug")

            fields = {
                "practice_zone": item.get("practice_zone"),
                "resolution": item.get("resolution"),
                "image": item.get("image"),
                "gif": item.get("gif"),
                "video": item.get("video"),
            }

            exercise, created = Exercise.objects.get_or_create(
                slug=slug,
                defaults=fields,
            )

            if not created:
                for attr, value in fields.items():
                    setattr(exercise, attr, value)
                exercise.save()

            for lang_code, trans in translations.items():
                exercise.set_current_language(lang_code)
                exercise.name = trans.get("name", "")
                exercise.description = trans.get("description", "")
                exercise.save()

            if created:
                created_count += 1
            else:
                updated_count += 1

        return created_count, updated_count

    def handle(self, *args, **options):
        fixture_file = options["fixture_file"]

        try:
            with open(fixture_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            with transaction.atomic():
                created_count, updated_count = self.upsert(data)

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Done — {created_count} created, {updated_count} updated."
                )
            )

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"❌ Import failed, nothing was saved: {e}")
            )