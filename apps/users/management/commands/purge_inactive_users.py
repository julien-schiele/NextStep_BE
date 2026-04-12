from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.users.models import User
from django.db.models import Q


class Command(BaseCommand):
    help = "Delete users inactive for more than 30 days"

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - timedelta(days=30)
        qs = User.objects.filter(
            Q(last_login__lt=cutoff)
            | Q(last_login__isnull=True, date_joined__lt=cutoff),
            is_staff=False,
            is_superuser=False,
        ).exclude(
            email__endswith="@nextstep.com"
        )  # keep demo accounts
        count = qs.count()
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} inactive user(s)"))
