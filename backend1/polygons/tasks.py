import requests
import json
import logging
from celery import shared_task
from django.conf import settings
from .models import Polygon, InvalidPolygon
from kafka import KafkaConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


logger = logging.getLogger(__name__)


BACKEND2_URL = "http://backend2:8001/check/"
KAFKA_TOPIC = "polygon_check_result"
KAFKA_SERVER = "kafka:9092"


@shared_task
def send_polygon_for_validation(polygon_id):
    try:
        polygon = Polygon.objects.get(id=polygon_id)
        data = {
            "name": polygon.name,
            "coordinates": json.loads(polygon.coordinates.json),
        }
        response = requests.post(BACKEND2_URL, json=data)

        if response.status_code == 200:
            logger.info(f"Полигон {polygon.name} отправлен на проверку")
        else:
            logger.error(f"Ошибка при отправке полигона: {response.text}")

    except Exception as e:
        logger.error(f"Ошибка Celery-задачи send_polygon_for_validation: {e}")


@shared_task
def process_polygon_validation_results():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    channel_layer = get_channel_layer()

    for message in consumer:
        result = message.value
        polygon_data = result.get("polygon")
        status = result.get("status")

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

            print("WebSocket отправка:", json.dumps(message, indent=4))

            async_to_sync(channel_layer.group_send)(
                "polygon_notifications",
                {
                    "type": "send_polygon_notification",
                    "message": {
                        "status": "invalid",
                        "polygon": {
                            "name": invalid_polygon.name,
                            "coordinates": json.loads(invalid_polygon.coordinates.json),
                        },
                        "intersecting_polygons": intersecting_polygons
                    }
                }
            )
