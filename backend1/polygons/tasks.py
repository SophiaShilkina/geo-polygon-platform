from .logger import logger
from celery import shared_task
from .producer import KafkaMessageProducer
from .consumers import KafkaMessageConsumer


@shared_task(queue='backend1_queue')
def send_polygon_for_validation(polygon_data):
    try:
        producer = KafkaMessageProducer()
        producer.send_message(polygon_data)
        logger.info(f"Полигон {polygon_data['name']} отправлен на проверку. Kafka Offset: {result.offset}")

    except Exception as e:
        logger.error(f"Ошибка Celery1-задачи send_polygon_for_validation: {e}")


@shared_task(queue='backend1_queue')
def process_polygon_validation_results():
    try:
        consumer = KafkaMessageConsumer()
        consumer.consume_messages()

    except Exception as e:
        logger.error(f"Ошибка Kafka Consumer1: {e}")
