from django.apps import AppConfig
import threading
import logging


logger = logging.getLogger(__name__)


class PolygonsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polygons'
