#!/usr/bin/env bash
# Production deploy: build frontend, collect static, run migrations
set -e
cd "$(dirname "$0")"

echo "Building frontend..."
./build_frontend.sh

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Deploy complete. Run: gunicorn vuvoz.wsgi:application (or use docker-compose)"
