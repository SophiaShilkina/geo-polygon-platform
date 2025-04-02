from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Polygon
from .serializers import PolygonSerializer
from .logger import logger


class PolygonViewSet(viewsets.ModelViewSet):
    queryset = Polygon.objects.all()
    serializer_class = PolygonSerializer


def get_cached_polygons():
    cached_data = cache.get("polygons")
    if cached_data is None:
        logger.info('Данные из БД (кеш пуст)')
        polygons = Polygon.objects.all()
        serializer = PolygonSerializer(polygons, many=True)
        cached_data = serializer.data
        cache.set("polygons", cached_data, timeout=3600)
    else:
        logger.info('Данные из Redis (кэш найден)')
    return cached_data


@api_view(["GET"])
def get_polygons(request):
    polygons_data = get_cached_polygons()
    return Response(polygons_data)
