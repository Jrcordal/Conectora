#!/usr/bin/env bash
set -euo pipefail

python manage.py collectstatic --noinput
python manage.py migrate --noinput

exec gunicorn main_page.wsgi:application \
  --bind 0.0.0.0:$PORT \
  --workers 3 \
  --timeout 60 \
  --graceful-timeout 30 \
  --log-level debug \
  --access-logfile - \
  --access-logformat '%(h)s "%(r)s" %(s)s %(b)s %(M)sms "%(f)s" "%(a)s"' \
  --error-logfile - \
  --capture-output

