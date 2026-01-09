#!/bin/sh
set -e

# Apply database migrations and collect static files, then start gunicorn
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn family_harvest.wsgi:application --bind 0.0.0.0:8000
