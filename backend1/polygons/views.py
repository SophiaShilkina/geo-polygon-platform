from rest_framework import viewsets, status
from .models import Polygon, InvalidPolygon
from .serializers import PolygonSerializer, InvalidPolygonSerializer


class PolygonViewSet(viewsets.ModelViewSet):
    queryset = Polygon.objects.all()
    serializer_class = PolygonSerializer


class InvalidPolygonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InvalidPolygon.objects.all()
    serializer_class = InvalidPolygonSerializer
