#!/bin/sh
set -e

echo "Ожидаю базу данных ${DB_HOST}:${DB_PORT}..."
until python -c "import socket, os; socket.create_connection((os.environ.get('DB_HOST','db'), int(os.environ.get('DB_PORT','5432'))), timeout=2)" 2>/dev/null; do
    echo "  база ещё не готова, жду..."
    sleep 2
done
echo "База доступна."

python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3