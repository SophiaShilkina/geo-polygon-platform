from kafka import KafkaProducer
import json
from django.conf import settings


class KafkaMessageProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send_polygon_for_check(self, message):
        self.producer.send("polygon_check_request", message)
        self.producer.flush()
        logger.info(f"Сообщение отправлено в Kafka (продюсер1): {message}")
