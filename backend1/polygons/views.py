from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Polygon, InvalidPolygon
from .serializers import PolygonSerializer, InvalidPolygonSerializer
from django.core.cache import cache
from django.http import JsonResponse


class PolygonViewSet(viewsets.ModelViewSet):
    queryset = Polygon.objects.all()
    serializer_class = PolygonSerializer


class InvalidPolygonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InvalidPolygon.objects.all()
    serializer_class = InvalidPolygonSerializer


class PolygonListView(APIView):
    def get(self, request):
        cache_key = "polygons_list"
        cached_polygons = cache.get(cache_key)

        if cached_polygons is not None:
            print("Получаем данные из кеша")
            return Response(cached_polygons, status=status.HTTP_200_OK)

        print("Получаем данные из БД")
        polygons = Polygon.objects.all()
        serializer = PolygonSerializer(polygons, many=True)
        cache.set(cache_key, serializer.data, timeout=60*5)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PolygonCreateView(APIView):
    def post(self, request):
        serializer = PolygonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete("polygons_list")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PolygonDeleteView(APIView):
    def delete(self, request, pk):
        try:
            polygon = PolygonModel.objects.get(pk=pk)
            polygon.delete()
            cache.delete("polygons_list")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PolygonModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
