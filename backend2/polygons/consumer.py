import json
import logging
from kafka import KafkaConsumer, KafkaProducer
from django.conf import settings
from django.contrib.gis.geos import Polygon as GeoPolygon
from .models import Polygon


logger = logging.getLogger(__name__)


def check_polygon_intersection(polygon_data):
    new_polygon = GeoPolygon(polygon_data['coordinates'])
    existing_polygons = Polygon.objects.all()
    intersecting_polygons = []

    for existing_polygon in existing_polygons:
        if new_polygon.intersects(existing_polygon.coordinates):
            intersecting_polygons.append({
                "name": existing_polygon.name,
                "coordinates": json.loads(existing_polygon.coordinates.json),
            })

    return intersecting_polygons


def start_polygon_check_consumer():
    consumer = KafkaConsumer(
        settings.KAFKA_TOPIC,
        bootstrap_servers=settings.KAFKA_SERVER,
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

    logger.info("Kafka Consumer запущен и ожидает сообщений...")

    for message in consumer:
        try:
            polygon_data = message.value
            logger.info(f"Получен полигон для проверки: {polygon_data['name']}")

            intersecting_polygons = check_polygon_intersection(polygon_data)

            result = {
                "polygon": polygon_data,
                "status": "invalid" if intersecting_polygons else "valid",
                "intersecting_polygons": intersecting_polygons
            }

            send_check_result(result)

        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")


def send_check_result(result):
    producer = KafkaProducer(
        bootstrap_servers='kafka:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    producer.send('polygon_check_result', result)
    logger.info(f"Результат проверки отправлен: {result}")
