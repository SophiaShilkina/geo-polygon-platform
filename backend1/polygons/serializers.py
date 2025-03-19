import logging
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Polygon as GeoPolygon
from .models import Polygon, PolygonUserAssignment, InvalidPolygon


User = get_user_model()

logger = logging.getLogger(__name__)


class PolygonSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)

    class Meta:
        model = Polygon
        fields = ['id', 'name', 'coordinates', 'crosses_antimeridian', 'users']

    @staticmethod
    def validate_coordinates(value):
        if len(value) < 3:
            raise serializers.ValidationError("Полигон должен содержать как минимум 3 точки.")

        first_point = value[0]
        last_point = value[-1]

        if first_point != last_point:
            value.append(first_point)
            logger.warning(f"Полигон не был замкнут. Первая точка {first_point} добавлена в конец для замыкания.")

        return value

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
