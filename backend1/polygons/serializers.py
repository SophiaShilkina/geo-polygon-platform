import logging
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Polygon as GeoPolygon
from .models import Polygon, PolygonUserAssignment, InvalidPolygon
from .tasks import send_polygon_for_validation


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

        if len(value) == 3 and first_point == last_point:
            raise serializers.ValidationError("Полигон должен содержать как минимум 3 незамкнутые точки.")

        if first_point != last_point:
            new_value = value + [first_point]
            logger.info(f"Полигон не был замкнут. Первая точка {first_point} добавлена в конец для замыкания.")
            value = new_value

        if has_duplicate_coordinates(value):
            raise serializers.ValidationError("Полигон не должен содержать повторяющиеся координаты, "
                                              "кроме замыкающих точек.")

        return value

    def create(self, validated_data):
        polygon = GeoPolygon(validated_data['coordinates'])

        instance = Polygon(name=validated_data['name'], coordinates=polygon)
        instance.save()
        send_polygon_for_validation.delay(instance.id)

        return instance


def has_duplicate_coordinates(coordinates):
    middle_coords = coordinates[1:]
    middle_coords_tuples = [tuple(coord) for coord in middle_coords]
    return len(middle_coords_tuples) != len(set(middle_coords_tuples))


class PolygonUserAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolygonUserAssignment
        fields = '__all__'


class InvalidPolygonSerializer(serializers.ModelSerializer):
    intersecting_polygons = PolygonSerializer(many=True, read_only=True)

    class Meta:
        model = InvalidPolygon
        fields = ['id', 'name', 'coordinates', 'reason', 'intersecting_polygons', 'created_at']
