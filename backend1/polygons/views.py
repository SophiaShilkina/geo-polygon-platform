from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Polygon, InvalidPolygon
from .serializers import PolygonSerializer, InvalidPolygonSerializer


class PolygonViewSet(viewsets.ModelViewSet):
    queryset = Polygon.objects.all()
    serializer_class = PolygonSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        polygon = serializer.save()
        check_polygon_intersection.delay(polygon.id)


class InvalidPolygonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InvalidPolygon.objects.all()
    serializer_class = InvalidPolygonSerializer
    permission_classes = [IsAuthenticated]
