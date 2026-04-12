# management/commands/send_cron_alert.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import subprocess


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("task_name", type=str)
        parser.add_argument("--log", type=str, default="/var/log/nextstep_cron.log")

    def handle(self, *args, **options):
        task_name = options["task_name"]
        log_path = options["log"]

        # Retrieve the last 20 lines of the log
        try:
            log_tail = subprocess.check_output(
                ["tail", "-n", "20", log_path]
            ).decode()
        except Exception:
            log_tail = "Unable to read the log."

        send_mail(
            subject=f"❌ Cron failed: {task_name}",
            message=f"The task `{task_name}` has failed on the VPS.\n\nLast lines of log :\n\n{log_tail}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
        )
        self.stdout.write(f"Alert sent for {task_name}")