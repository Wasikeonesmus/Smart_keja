#!/bin/bash
# Startup script for Render deployment
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Starting application with gunicorn..."
exec gunicorn smartkeja.wsgi:application --bind 0.0.0.0:${PORT:-10000}

