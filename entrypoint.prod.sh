#!/usr/bin/env bash
set -euo pipefail

python manage.py collectstatic --noinput
python manage.py migrate --noinput

exec gunicorn main_page.wsgi:application \
  --bind 0.0.0.0:${PORT:-8080} \
  --workers ${WEB_CONCURRENCY:-3} \
  --log-level debug \
  --access-logfile - \
  --error-logfile - \
  --capture-output
