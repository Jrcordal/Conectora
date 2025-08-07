from .settings import *
from apps.workers.celery import app as celery_app

__all__ = ('celery_app',)