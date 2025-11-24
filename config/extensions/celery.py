from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("config.celery")
app.conf.enable_utc = False
app.conf.result_backend = "django-db"
app.conf.result_serializer = "json"
app.conf.result_extended = True

# app.config_from_envvar(settings.CELERY_BROKER_URL)
app.config_from_object(settings, namespace="CELERY")

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    "sync-ticker-types-daily": {
        "task": "core.tasks.sync_ticker_types_task",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2:00 AM
        "args": ("stocks", "us"),  # Default args: asset_class="stocks", locale="us"
    },
    "create-daily-ticker-summaries": {
        "task": "core.tasks.create_daily_ticker_summaries_task",
        "schedule": crontab(minute="*/30"),  # Run every 30 minutes
    },
}