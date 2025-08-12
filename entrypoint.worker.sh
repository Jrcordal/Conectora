# entrypoint.worker.sh
#!/usr/bin/env bash
set -e
exec celery -A main_page worker -l info
#                ^^^^^^^^^  cambia por el módulo donde esté tu celery.py
