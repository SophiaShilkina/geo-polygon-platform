from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Polygon as GeoPolygon
from .models import Polygon, PolygonUserAssignment, InvalidPolygon


User = get_user_model()


class PolygonSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)

    class Meta:
        model = Polygon
        fields = ['id', 'name', 'coordinates', 'crosses_antimeridian', 'users']

    def create(self, validated_data):
        coordinates = validated_data.pop('coordinates')
        polygon = GeoPolygon(coordinates)
        validated_data['coordinates'] = polygon

        return super().create(validated_data)


class PolygonUserAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolygonUserAssignment
        fields = '__all__'


class InvalidPolygonSerializer(serializers.ModelSerializer):
    intersecting_polygons = PolygonSerializer(many=True, read_only=True)

    class Meta:
        model = InvalidPolygon
        fields = ['id', 'name', 'coordinates', 'reason', 'intersecting_polygons', 'created_at']
