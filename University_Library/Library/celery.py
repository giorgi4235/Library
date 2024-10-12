# your_project/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

app = Celery('your_project')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Define the periodic task schedule
app.conf.beat_schedule = {
    'send-due-date-notifications': {
        'task': 'your_app.tasks.send_due_date_notifications',
        'schedule': crontab(hour=9, minute=0),  # Run daily at 9 AM
    },
}
