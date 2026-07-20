#!/bin/sh
set -e

# ==============================================================================
# Script Name: entrypoint.sh
# Description: Docker entrypoint script for Django applications. Handles database
#              readiness checks, migrations, static files, superuser creation,
#              and WSGI server startup.
# ==============================================================================

# ------------------------------------------------------------------------------
# Wait for Database Availability
# ------------------------------------------------------------------------------
# Args:
#   DB_HOST (str): Hostname or IP of the database server (default: 'db').
#   DB_PORT (int): Port number of the database server (default: 5432).
#
# Raises:
#   TimeoutError: Retries every 2 seconds until connection is established.
# ------------------------------------------------------------------------------
echo "Waiting for database ${DB_HOST}:${DB_PORT}..."
until python -c "import socket, os; socket.create_connection((os.environ.get('DB_HOST','db'), int(os.environ.get('DB_PORT','5432'))), timeout=2)" 2>/dev/null; do
    echo "  database is not ready yet, waiting..."
    sleep 2
done
echo "Database is available."

# Apply database schema migrations non-interactively
python manage.py migrate --noinput

# Collect static assets into STATIC_ROOT
python manage.py collectstatic --noinput

# ------------------------------------------------------------------------------
# Conditional Superuser Provisioning
# ------------------------------------------------------------------------------
# Environment Variables:
#   DJANGO_SUPERUSER_EMAIL (str): Superuser email address.
#   DJANGO_SUPERUSER_PASSWORD (str): Superuser password.
# ------------------------------------------------------------------------------
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if email and password and not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password, name='Admin')
    print('Superuser created:', email)
else:
    print('Superuser already exists or environment variables are not set — skipping.')
"

# Populate database with initial seed/reference data
python manage.py fill_db

# ------------------------------------------------------------------------------
# Application Server Execution
# ------------------------------------------------------------------------------
# Replaces the shell process with Gunicorn WSGI server.
# Args:
#   PORT (int): Port to bind the server to (default: 8000).
#   workers (int): Number of worker processes (default: 3).
# ------------------------------------------------------------------------------
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3