"""
Celery Configuration for Background Jobs
"""

from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Redis Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# Initialize Celery with Redis broker
celery_app = Celery(
    'kisansathi',
    broker=f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
    backend=f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
    include=['tasks']  # Auto-discover tasks
)

# Celery Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic Tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    'check-weather-alerts-every-hour': {
        'task': 'tasks.check_weather_alerts',
        'schedule': crontab(minute=0),
    },
    'send-crop-reminders-daily': {
        'task': 'tasks.send_crop_reminders',
        'schedule': crontab(hour=6, minute=0),
    },
    'cleanup-old-cache-daily': {
        'task': 'tasks.cleanup_cache',
        'schedule': crontab(hour=2, minute=0),
    },
    'generate-reports-weekly': {
        'task': 'tasks.generate_reports',
        'schedule': crontab(day_of_week=0, hour=0, minute=0),
    },
}
