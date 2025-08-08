# entrypoint.worker.sh
#!/usr/bin/env bash
set -e
exec celery -A apps.workers.celery worker -l info
#                ^^^^^^^^^  cambia por el módulo donde esté tu celery.py
