import os
from celery import Celery
from polygons.topics import create_kafka_topics
from polygons.logger import logger
from celery.signals import worker_ready


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend1.settings')

app = Celery('backend1')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.task_default_queue = 'backend1_queue'

try:
    create_kafka_topics()
except Exception as e:
    logger.error(f"Ошибка создания Kafka топиков: {e}")

app.autodiscover_tasks()


@worker_ready.connect
def at_start(sender, **kwargs):
    with sender.app.connection() as conn:
        sender.app.send_task('polygons.tasks.process_polygon_validation_results', connection=conn)
