#!/bin/bash
set -e  # stop if a command fails

# Wait for DB to be ready
echo "Waiting for database..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done
echo "Database ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Upsert exercises and programs on every deploy (idempotent)
echo "Upserting exercises and programs..."
python manage.py upsert_exercises apps/programs/fixtures/exercises.json
python manage.py upsert_programs apps/programs/fixtures/new_programs.json

# Load privacy policies only if none exist (managed via admin after first deploy)
POLICY_COUNT=$(python manage.py shell -c "from apps.utils.models import PrivacyPolicy; print(PrivacyPolicy.objects.count())" | grep -Eo '^[0-9]+$')
if [ "$POLICY_COUNT" -eq 0 ]; then
    echo "Loading initial privacy policies..."
    python manage.py load_privacy apps/utils/fixtures/privacy_en.md --lang en
    python manage.py load_privacy apps/utils/fixtures/privacy_es.md --lang es
    python manage.py load_privacy apps/utils/fixtures/privacy_fr.md --lang fr
fi

# Seed demo data only on first deploy (cron handles weekly reset with --tracking-only)
DEMO_SEEDED=$(python manage.py shell -c "from apps.users.models import User; print(User.objects.filter(email='demo1@nextstep.com').exists())" | grep -Eo 'True|False')
if [ "$DEMO_SEEDED" = "False" ]; then
    echo "Seeding demo data..."
    python manage.py seed_demo_data
fi

# Compile translation messages (if needed)
python manage.py compilemessages

# Run the command passed to the container
# Default is runserver
if [ "$1" = "runserver" ]; then
    echo "Starting Django server..."
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "Collecting static files..."
    python manage.py collectstatic --no-input

    # Allow running arbitrary commands, e.g. bash
    exec "$@"
fi
