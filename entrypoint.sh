#!/bin/sh
set -e

echo "Ожидаю базу данных ${DB_HOST}:${DB_PORT}..."
until python -c "import socket, os; socket.create_connection((os.environ.get('DB_HOST','db'), int(os.environ.get('DB_PORT','5432'))), timeout=2)" 2>/dev/null; do
    echo "  база ещё не готова, жду..."
    sleep 2
done
echo "База доступна."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if email and password and not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password, name='Admin')
    print('Суперпользователь создан:', email)
else:
    print('Суперпользователь уже существует или переменные не заданы — пропускаю.')
"


python manage.py fill_db

exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3