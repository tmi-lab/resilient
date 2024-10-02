#!/bin/bash

# Check if DEBUG is set to true
# Convert DEBUG value to lowercase
DEBUG_LOWER=$(echo "$DEBUG" | tr '[:upper:]' '[:lower:]')

if [[ "$DEBUG_LOWER" = "true" ]]; then
    # Collect static files
    python manage.py collectstatic --noinput
fi

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate --run-syncdb

# Start the Gunicorn server
gunicorn config.wsgi:application --bind 0.0.0.0:8000
