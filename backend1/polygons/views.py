from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Polygon, InvalidPolygon
from .serializers import PolygonSerializer, InvalidPolygonSerializer
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
from .tasks import refresh_polygon_cache


class PolygonViewSet(viewsets.ModelViewSet):
    queryset = Polygon.objects.all()
    serializer_class = PolygonSerializer

    def list(self, request, *args, **kwargs):
        cache_key = 'polygons_list'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=3600)

        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()
        refresh_polygon_cache.delay()

    def perform_update(self, serializer):
        serializer.save()
        refresh_polygon_cache.delay()

    def perform_destroy(self, instance):
        instance.delete()
        refresh_polygon_cache.delay()


class InvalidPolygonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InvalidPolygon.objects.all()
    serializer_class = InvalidPolygonSerializer

    def list(self, request, *args, **kwargs):
        cache_key = 'invalid_polygons_list'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=3600)

        return Response(serializer.data)
