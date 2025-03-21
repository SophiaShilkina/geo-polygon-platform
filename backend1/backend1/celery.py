import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend1.settings')

app = Celery('backend1')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.task_default_queue = 'backend1_queue'
app.autodiscover_tasks()
