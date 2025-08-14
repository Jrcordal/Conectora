#!/usr/bin/env bash
set -euo pipefail
exec celery -A main_page worker -l INFO -c 3
