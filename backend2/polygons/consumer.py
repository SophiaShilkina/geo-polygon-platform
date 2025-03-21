from kafka import KafkaConsumer
import json
from django.conf import settings
from .logger import logger


class KafkaMessageConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            "polygon_check_request",
            bootstrap_servers=settings.KAFKA_BROKER_URL,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            group_id="polygon_group_backend2",
            auto_offset_reset="earliest"
        )

    def consume_messages(self):
        for message in self.consumer:
            polygon_data = message.value
            logger.info(f"Получен полигон из Kafka: {polygon_data}")

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

            yield result
