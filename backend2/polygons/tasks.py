from kafka import KafkaConsumer, KafkaProducer
from celery import shared_task
import json
import logging
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from .models import Polygon


@shared_task
def process_polygon_from_kafka():
    try:
        logging.info("Backend 2: Ожидание полигонов в Kafka...")

        consumer = KafkaConsumer(
            "polygon_check_request",
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset='earliest',
            group_id="polygon_group_backend2"
        )

        producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        logger.info("Backend 2: Kafka Consumer запущен и ожидает сообщения...")

        for message in consumer:
            polygon_data = message.value
            logging.info(f"Получен полигон из Kafka: {polygon_data}")

            new_polygon = GEOSGeometry(json.dumps(polygon_data["coordinates"]))
            intersecting_polygons = Polygon.objects.filter(coordinates__intersects=new_polygon)

            if intersecting_polygons.exists():
                result = {
                    "status": "invalid",
                    "polygon": polygon_data,
                    "intersecting_polygons": [
                        {"name": p.name, "coordinates": json.loads(p.coordinates.json)}
                        for p in intersecting_polygons
                    ],
                }
            else:
                result = {
                    "status": "valid",
                    "polygon": polygon_data,
                }

            producer.send("polygon_check_result", result)
            producer.flush()
            logging.info(f"Celery2: Отправлен результат в Kafka: {result}")

    except Exception as e:
        logger.error(f"Ошибка Kafka Consumer: {e}")
