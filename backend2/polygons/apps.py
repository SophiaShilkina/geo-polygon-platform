from django.apps import AppConfig
import threading
import logging


logger = logging.getLogger(__name__)


class PolygonsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polygons'

    def ready(self):
        logger.info("Инициализация PolygonsConfig...")
        from .consumer import start_polygon_check_consumer

        logger.info("Запуск Kafka Consumer...")
        consumer_thread = threading.Thread(target=start_polygon_check_consumer, daemon=True)
        consumer_thread.start()
