#!/bin/bash
set -e

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Register the service
python ./register_service.py

# Start the application
exec gunicorn --bind 0.0.0.0:8000 authenService.wsgi:application --reload --access-logfile '-' --error-logfile '-'