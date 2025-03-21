from .producer import KafkaMessageProducer
from .consumer import KafkaMessageConsumer
from celery import shared_task
import json
from .logger import logger
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from .models import Polygon


@shared_task(queue='backend2_queue')
def process_polygon_from_kafka():
    try:
        consumer = KafkaMessageConsumer()
        producer = KafkaMessageProducer()

        logger.info("Задача Celery2 запущена. Ожидание сообщений из Kafka...")

        for result in consumer.consume_messages():
            producer.send_polygon_result(result)
            logger.info(f"Результат отправлен в Kafka: {result}")

    except Exception as e:
        logger.error(f"Ошибка в задаче Celery2: {e}")
