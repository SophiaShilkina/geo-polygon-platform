import json
from channels.generic.websocket import AsyncWebsocketConsumer
from kafka import KafkaConsumer
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .logger import logger


class PolygonConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("polygon_notifications", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("polygon_notifications", self.channel_name)

    async def send_polygon_notification(self, event):
        await self.send(text_data=json.dumps(event["message"]))


class KafkaMessageConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            "polygon_check_result",
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            group_id="polygon_group_backend1",
            auto_offset_reset="earliest"
        )

    def consume_messages(self):
        from .models import Polygon, InvalidPolygon
        from django.contrib.gis.geos import Polygon as GeoPolygon

        channel_layer = get_channel_layer()

        for message in self.consumer:
            result = message.value
            polygon_data = result.get("polygon")
            status = result.get("status")

            logger.info(f"Backend 1 получил результат: {status} для {polygon_data['name']}")

            try:
                coordinates = polygon_data["coordinates"]["coordinates"][0]
                new_polygon = GeoPolygon(coordinates)

                if status == "invalid":
                    invalid_polygon = InvalidPolygon.objects.create(
                        name=polygon_data["name"],
                        coordinates=new_polygon,
                        reason="Пересечение с другими полигонами"
                    )

                    intersecting_polygons = []
                    for poly in result["intersecting_polygons"]:
                        p, _ = Polygon.objects.get_or_create(
                            name=poly["name"],
                            coordinates=GeoPolygon(poly["coordinates"]["coordinates"][0])
                        )
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
                    polygon = Polygon.objects.create(
                        name=polygon_data["name"],
                        coordinates=new_polygon,
                        crosses_antimeridian=result.get("crosses_antimeridian", False)
                    )
                    polygon.save()
                    logger.info(f"Полигон {polygon_data['name']} добавлен в базу данных.")

            except Exception as e:
                logger.error(f"Ошибка при обработке полигона: {e}")
