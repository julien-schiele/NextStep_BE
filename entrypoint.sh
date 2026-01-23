#!/bin/bash
# Entrypoint for NextStep Django dev

# Wait for DB to be ready
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "Database ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Load initial data (fixtures)
echo "No initial data to load yet..."


# Run the command passed to the container
# Default is runserver
if [ "$1" = "runserver" ]; then
    echo "Starting Django server..."
    exec python manage.py runserver 0.0.0.0:8000
else
    # Allow running arbitrary commands, e.g. bash
    exec "$@"
fi
