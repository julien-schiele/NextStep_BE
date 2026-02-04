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

# Load initial data (custom JSON)
# Only if the tables are empty (idempotent)
EXERCISE_COUNT=$(python manage.py shell -c "from apps.programs.models import Exercise; print(Exercise.objects.count())" | grep -Eo '^[0-9]+$')
if [ "$EXERCISE_COUNT" -eq 0 ]; then
    echo "Loading initial exercises and programs..."
    python manage.py load_exercises apps/programs/fixtures/exercises.json
    python manage.py load_programs apps/programs/fixtures/programs.json
fi

# Compile translation messages (if needed)
python manage.py compilemessages

# Run the command passed to the container
# Default is runserver
if [ "$1" = "runserver" ]; then
    echo "Starting Django server..."
    exec python manage.py runserver 0.0.0.0:8000
else
    # Allow running arbitrary commands, e.g. bash
    exec "$@"
fi
