from uuid import uuid4
from django.db import transaction
from django.core.management.base import BaseCommand
from parler.utils.context import switch_language
from apps.utils.models import PrivacyPolicy
import markdown
import os


class Command(BaseCommand):
    help = "Load PrivacyPolicy from Markdown file(s) (atomic)"

    def add_arguments(self, parser):
        parser.add_argument(
            "md_file",
            type=str,
            help="Path to the Markdown file containing the privacy policy",
        )
        parser.add_argument(
            "--lang", type=str, default="en", help="Language code for this translation"
        )
        parser.add_argument(
            "--short_marker",
            type=str,
            default="<!-- SHORT -->",
            help="Marker in Markdown file separating short/long text",
        )

    def create_from_md(self, md_file: str, lang: str, short_marker: str):
        """Parse Markdown, delete existing entries, and create new PrivacyPolicy"""
        if not os.path.exists(md_file):
            raise FileNotFoundError(f"File not found: {md_file}")

        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        if short_marker in content:
            long_md, short_md = content.split(short_marker, 1)
        else:
            short_md, long_md = content[:500], content  # fallback

        short_text = markdown.markdown(short_md.strip())
        long_text = markdown.markdown(long_md.strip())

        with transaction.atomic():
            policy = PrivacyPolicy.objects.first()
            if not policy:
                policy = PrivacyPolicy.objects.create()
            with switch_language(policy, lang):
                policy.short_text = short_text
                policy.long_text = long_text
                policy.save()

        return policy

    def handle(self, *args, **options):
        md_file = options["md_file"]
        lang = options["lang"]
        short_marker = options["short_marker"]

        try:
            policy = self.create_from_md(md_file, lang, short_marker)
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ PrivacyPolicy successfully created for lang '{lang}' (UUID={policy.id})"
                )
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"❌ Import failed, nothing was saved: {e}")
            )
