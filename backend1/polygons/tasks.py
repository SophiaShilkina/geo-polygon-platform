import requests
import json
import logging
from celery import shared_task
from django.conf import settings
from .models import Polygon, InvalidPolygon
from kafka import KafkaConsumer, KafkaProducer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


logger = logging.getLogger(__name__)


@shared_task
def send_polygon_for_validation(polygon_id):
    try:
        polygon = Polygon.objects.get(id=polygon_id)
        data = {
            "id": polygon.id,
            "name": polygon.name,
            "coordinates": json.loads(polygon.coordinates.json),
        }

        producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        )

        future = producer.send("polygon_check_request", data)
        result = future.get(timeout=15)
        producer.flush()
        logger.info(f"Полигон {polygon.name} отправлен на проверку. Kafka Offset: {result.offset}")

    except Exception as e:
        logger.error(f"Ошибка Celery-задачи send_polygon_for_validation: {e}")


@shared_task
def process_polygon_validation_results():
    try:
        consumer = KafkaConsumer(
            "polygon_check_result",
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset='earliest',
            group_id="polygon_validator_backend1"
        )

        channel_layer = get_channel_layer()

        for message in consumer:
            result = message.value
            polygon_data = result.get("polygon")
            status = result.get("status")

            logger.info(f"Backend 1 получил результат: {status} для {polygon_data['name']}")

            if status == "invalid":
                invalid_polygon = InvalidPolygon.objects.create(
                    name=polygon_data["name"],
                    coordinates=polygon_data["coordinates"],
                    reason="Пересечение с другими полигонами"
                )

                intersecting_polygons = []
                for poly in result["intersecting_polygons"]:
                    p, _ = Polygon.objects.get_or_create(name=poly["name"], coordinates=poly["coordinates"])
                    invalid_polygon.intersecting_polygons.add(p)
                    intersecting_polygons.append({
                        "name": p.name,
                        "coordinates": json.loads(p.coordinates.json)
                    })

                invalid_polygon.save()

                message = {
                    "status": "invalid",
                    "polygon": {
                        "name": invalid_polygon.name,
                        "coordinates": json.loads(invalid_polygon.coordinates.json),
                    },
                    "intersecting_polygons": intersecting_polygons
                }

                logger.info(f"Отправка WebSocket: {message}")

                async_to_sync(channel_layer.group_send)(
                    "polygon_notifications",
                    {
                        "type": "send_polygon_notification",
                        "message": message
                    }
                )
            else:
                Polygon.objects.create(
                    name=polygon_data["name"],
                    coordinates=polygon_data["coordinates"]
                )
                logger.info(f"Полигон {polygon_data['name']} добавлен в базу данных.")

    except Exception as e:
        logger.error(f"Ошибка Kafka Consumer: {e}")
