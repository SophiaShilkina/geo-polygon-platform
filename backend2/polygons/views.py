from rest_framework import status, views
from rest_framework.response import Response
from django.contrib.gis.geos import GEOSGeometry
from .models import Polygon
from .serializers import PolygonSerializer
from .tasks import process_polygon_from_kafka
import json
import logging


logger = logging.getLogger(__name__)

class PolygonCheckView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = PolygonSerializer(data=request.data)
        if serializer.is_valid():
            new_polygon = GEOSGeometry(json.dumps(request.data['coordinates']))
            process_polygon_from_kafka.delay()

            return Response({"message": "Полигон отправлен в обработку"}, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
