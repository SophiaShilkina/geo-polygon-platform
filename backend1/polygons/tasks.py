from celery import shared_task
from .producer import KafkaMessageProducer
from .consumers import KafkaMessageConsumer
from .logger import logger
from django.core.cache import cache
from .models import PolygonModel
from .serializers import PolygonSerializer


@shared_task(queue='backend1_queue')
def send_polygon_for_validation(polygon_data):
    try:
        producer = KafkaMessageProducer()
        producer.send_polygon_for_check(polygon_data)
        logger.info(f"Полигон {polygon_data['name']} отправлен на проверку.")

    except Exception as e:
        logger.error(f"Ошибка Celery1-задачи send_polygon_for_validation: {e}")


@shared_task(queue='backend1_queue')
def process_polygon_validation_results():
    try:
        consumer = KafkaMessageConsumer()
        consumer.consume_messages()

    except Exception as e:
        logger.error(f"Ошибка Kafka Consumer1: {e}")


@shared_task
def update_polygon_cache():
    print("Фоновое обновление кеша")
    polygons = PolygonModel.objects.all()
    serializer = PolygonSerializer(polygons, many=True)
    cache.set("polygons_list", serializer.data, timeout=60*10)
