#!/usr/bin/env bash
set -e

# Lanza el worker de Celery usando la app registrada en __init__.py
exec celery -A main_page worker -l info
