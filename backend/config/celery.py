"""
Celery configuration
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('ecommerce_optimizer')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Register periodic tasks
app.conf.beat_schedule = {
    # Cleanup expired onboarding sessions
    'cleanup-expired-onboarding-sessions': {
        'task': 'onboarding.tasks.cleanup_expired_sessions',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
    # Add other periodic tasks here
}
