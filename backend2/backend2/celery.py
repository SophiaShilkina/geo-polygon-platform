import os
from celery import Celery
from celery.signals import worker_ready


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend2.settings")

app = Celery("backend2")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.task_default_queue = 'backend2_queue'
app.autodiscover_tasks()


@worker_ready.connect
def at_start(sender, **kwargs):
    with sender.app.connection() as conn:
        sender.app.send_task('polygons.tasks.process_polygon_from_kafka', connection=conn)
