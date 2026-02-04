import json
from django.db import transaction
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.programs.models import Program


class Command(BaseCommand):
    help = "Create Program model entries from JSON fixture (atomic)"

    def add_arguments(self, parser):
        parser.add_argument(
            "fixture_file", type=str, help="Path to the JSON fixture file"
        )

    def create(self, data):
        for idx, item in enumerate(data, start=1):
            translations = item.get("translations", {})
            if not translations:
                raise ValueError(f"ITEM #{idx} has no translations")

            en_name = translations.get("en", {}).get("name", "")
            if not en_name:
                raise ValueError(f"ITEM #{idx} has no EN name (required for slug)")

            slug = slugify(en_name)

            program = Program.objects.create(
                slug=slug,
                focus=item.get("focus"),
                level=item.get("level"),
                is_public=item.get("is_public", True),
                content=item.get("content"),
                focus_axes=item.get("focus_axes", []),
                cycle_rhythm=item.get("cycle_rhythm", {}),
            )

            for lang_code, trans in translations.items():
                program.set_current_language(lang_code)
                program.name = trans.get("name", "")
                program.description = trans.get("description", "")
                program.realistic_if = trans.get("realistic_if", [])
                program.not_realistic_if = trans.get("not_realistic_if", [])

                program.save()

    def handle(self, *args, **options):
        fixture_file = options["fixture_file"]

        try:
            with open(fixture_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 🔒 atomic: delete + recreate = all or nothing
            with transaction.atomic():
                Program.objects.all().delete()
                self.create(data)

            self.stdout.write(
                self.style.SUCCESS(
                    "✅ Successfully loaded ALL Program entries (atomic)."
                )
            )

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"❌ Import failed, nothing was saved: {e}")
            )
