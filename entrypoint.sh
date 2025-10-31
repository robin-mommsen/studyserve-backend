#!/bin/sh

set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting Django QCluster..."
python manage.py qcluster &

echo "Starting django-mailer..."
python manage.py runmailer &

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
