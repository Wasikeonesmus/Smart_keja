#!/bin/bash
# Startup script for Render deployment
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Starting application..."
exec gunicorn smartkeja.wsgi:application

