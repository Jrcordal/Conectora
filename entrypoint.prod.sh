#!/usr/bin/env bash
set -euo pipefail

python manage.py collectstatic --noinput
python manage.py migrate --noinput

# usa exec para que gunicorn sea PID 1 y reciba señales,
# y saca access logs al STDOUT (se ven en Railway)
exec gunicorn main_page.wsgi:application \
  --bind 0.0.0.0:${PORT:-8080} \
  --workers ${WEB_CONCURRENCY:-3} \
  --access-logfile - \
  --error-logfile -
