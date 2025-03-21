import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend2.settings")

app = Celery("backend2")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.task_default_queue = 'backend2_queue'
app.autodiscover_tasks()
