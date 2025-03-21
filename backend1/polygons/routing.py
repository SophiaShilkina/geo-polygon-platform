from django.urls import re_path
from .consumers import PolygonConsumer


websocket_urlpatterns = [
    re_path(r'ws/polygons/$', PolygonConsumer.as_asgi()),
]
