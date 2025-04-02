from django.apps import AppConfig
from .tasks import process_polygon_from_kafka


class PolygonsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polygons'
