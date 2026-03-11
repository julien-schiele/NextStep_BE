"""
Management command: seed_demo_data
===================================
Creates demo users with realistic UserProgram / UserProgramSession /
UserProgramFeedback data so visitors can log in and explore the app.

Usage
-----
    # First run (or daily cron reset):
    python manage.py seed_demo_data

    # Keep existing Programs/Exercises, only reset user tracking data:
    python manage.py seed_demo_data --tracking-only

Cron (Railway / APScheduler / crontab)
---------------------------------------
    0 4 * * * python manage.py seed_demo_data --tracking-only
    # Runs at 04:00 UTC every day — resets demo sessions without
    # touching your Program/Exercise catalogue.

Demo credentials (display these on your login page)
----------------------------------------------------
    demo1@nextstep.com / Demo1234!
    demo2@nextstep.com / Demo1234!
    demo3@nextstep.com / Demo1234!
"""

import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.programs.models import Program
from apps.tracking.choices import Rating, Status, Usefunlness
from apps.tracking.models import UserProgram, UserProgramFeedback, UserProgramSession
from apps.users.models import User

# ---------------------------------------------------------------------------
# Config — tweak freely
# ---------------------------------------------------------------------------

DEMO_PASSWORD = "Demo1234!"

DEMO_USERS = [
    {"email": "demo1@nextstep.com", "first_name": "Alice", "last_name": "Demo"},
    {"email": "demo2@nextstep.com", "first_name": "Bob", "last_name": "Demo"},
    {"email": "demo3@nextstep.com", "first_name": "Charlie", "last_name": "Demo"},
]

# How many past sessions to generate per user (simulates mid-program progress)
SESSIONS_PER_USER = 6


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_or_create_demo_user(data: dict) -> User:
    user, created = User.objects.get_or_create(
        email=data["email"],
        defaults={
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "is_active": True,
        },
    )
    # Always reset password so it matches DEMO_PASSWORD after a wipe
    user.set_password(DEMO_PASSWORD)
    user.save(update_fields=["password"])
    return user


def _pick_program(index: int) -> Program | None:
    """
    Distribute demo users across available public programs.
    Falls back to any program if fewer than 3 are public.
    """
    qs = Program.objects.filter(is_public=True).order_by("created_at")
    if not qs.exists():
        qs = Program.objects.order_by("created_at")
    if not qs.exists():
        return None
    return qs[index % qs.count()]


def _build_session_snapshot(program: Program, session_in_cycle: int) -> dict:
    """
    Minimal snapshot derived from program.content so the session looks real.
    Adapt the key names to match your actual content schema.
    """
    content = program.content or {}
    sessions = content.get("sessions", [])

    if sessions and session_in_cycle <= len(sessions):
        raw = sessions[session_in_cycle - 1]
    else:
        raw = {"note": "auto-generated demo session"}

    return {
        "program_slug": program.slug,
        "cycle_session": session_in_cycle,
        "snapshot_at": timezone.now().isoformat(),
        "data": raw,
    }


def _seed_tracking_for_user(user: User, program: Program, session_count: int) -> None:
    """
    Creates one active UserProgram + N completed sessions + one feedback.
    Idempotent: wipes existing tracking data for this user first.
    """
    # Clean slate for this user's tracking data only
    UserProgram.objects.filter(user=user).delete()

    user_program = UserProgram.objects.create(
        user=user,
        program=program,
        status=Status.ACTIVE,
    )

    ratings = list(Rating.values)

    for i in range(1, session_count + 1):
        created_offset = timezone.now() - timedelta(days=(session_count - i + 1))
        session = UserProgramSession.objects.create(
            user_program=user_program,
            cycle_count=1,
            session_in_cycle=i,
            session_snapshot=_build_session_snapshot(program, i),
            rating=random.choice(ratings),
        )
        # Back-date created_at to make the timeline look realistic
        UserProgramSession.objects.filter(pk=session.pk).update(
            created_at=created_offset,
            updated_at=created_offset,
        )

    # Add feedback only for user 1 (others are mid-program, no feedback yet)
    if user.email == DEMO_USERS[0]["email"]:
        UserProgramFeedback.objects.create(
            user_program=user_program,
            usefulness=random.choice(list(Usefunlness.values)),
            would_repeat=True,
            comment="Great program, really enjoyed the progressive difficulty!",
        )


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------


class Command(BaseCommand):
    help = "Seed demo users + realistic tracking data (safe to run daily)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tracking-only",
            action="store_true",
            help="Only reset tracking data; do not touch Users (faster daily cron)",
        )

    def handle(self, *args, **options):
        tracking_only = options["tracking_only"]

        with transaction.atomic():
            users = []

            if tracking_only:
                # Fetch existing demo users — skip if not seeded yet
                for data in DEMO_USERS:
                    try:
                        users.append(User.objects.get(email=data["email"]))
                    except User.DoesNotExist:
                        self.stderr.write(
                            self.style.WARNING(
                                f"⚠️  Demo user {data['email']} not found — "
                                f"run without --tracking-only first."
                            )
                        )
                        return
            else:
                for data in DEMO_USERS:
                    users.append(_get_or_create_demo_user(data))
                self.stdout.write(f"✅ {len(users)} demo users ready.")

            for idx, user in enumerate(users):
                program = _pick_program(idx)
                if program is None:
                    self.stderr.write(
                        self.style.ERROR(
                            "❌ No Program found in DB. "
                            "Run load_programs first:\n"
                            "    python manage.py load_programs fixtures/programs.json"
                        )
                    )
                    return

                _seed_tracking_for_user(user, program, SESSIONS_PER_USER)
                self.stdout.write(
                    f"   ↳ {user.email} → program '{program.slug}' "
                    f"({SESSIONS_PER_USER} sessions seeded)"
                )

        self.stdout.write(self.style.SUCCESS("\n✅ Demo data seeded successfully.\n"))
        self.stdout.write("   Login credentials:")
        for data in DEMO_USERS:
            self.stdout.write(f"   • {data['email']} / {DEMO_PASSWORD}")
