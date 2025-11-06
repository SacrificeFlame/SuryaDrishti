from celery import Celery
from celery.schedules import crontab
from .config import settings

celery_app = Celery(
    "suryादrishti",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    'generate-forecasts-every-15min': {
        'task': 'app.tasks.forecast_tasks.generate_forecast_task',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'args': ('all_microgrids',)
    },
    'retrain-models-weekly': {
        'task': 'app.tasks.forecast_tasks.retrain_models_task',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),  # Sunday 2 AM
    },
}

