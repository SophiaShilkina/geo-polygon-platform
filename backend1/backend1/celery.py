import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend1.settings')

app = Celery('backend1')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
