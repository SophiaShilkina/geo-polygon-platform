from rest_framework import status, views
from rest_framework.response import Response
from django.contrib.gis.geos import GEOSGeometry
from .models import Polygon
from .serializers import PolygonSerializer
from kafka import KafkaProducer
import json


KAFKA_TOPIC = "polygon_check_result"
KAFKA_SERVER = "kafka:9092"


class PolygonCheckView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = PolygonSerializer(data=request.data)
        if serializer.is_valid():
            new_polygon = GEOSGeometry(json.dumps(request.data['coordinates']))

            intersecting_polygons = Polygon.objects.filter(coordinates__intersects=new_polygon)

            if intersecting_polygons.exists():
                result = {
                    "status": "invalid",
                    "polygon": serializer.data,
                    "intersecting_polygons": PolygonSerializer(intersecting_polygons, many=True).data
                }
            else:
                serializer.save()
                result = {
                    "status": "valid",
                    "polygon": serializer.data
                }

            producer = KafkaProducer(
                bootstrap_servers=KAFKA_SERVER,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            producer.send(KAFKA_TOPIC, result)
            producer.flush()

            return Response(result, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
