from django.apps import AppConfig
from .tasks import process_polygon_validation_results


class PolygonsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polygons'

    def ready(self):
        process_polygon_validation_results.delay()
