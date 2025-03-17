from django.contrib.auth import get_user_model
from django.contrib.gis.db import models


User = get_user_model()


class Polygon(models.Model):
    name = models.CharField(max_length=255)
    coordinates = models.PolygonField()
    crosses_antimeridian = models.BooleanField(default=False)
    users = models.ManyToManyField(User, through="PolygonUserAssignment", related_name="polygons", through_fields=("polygon", "user"),)

    def __str__(self):
        return self.name


class PolygonUserAssignment(models.Model):
    polygon = models.ForeignKey(Polygon, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="assigned_polygons")


class InvalidPolygon(models.Model):
    name = models.CharField(max_length=255)
    coordinates = models.PolygonField()
    reason = models.TextField()
    intersecting_polygons = models.ManyToManyField(Polygon, related_name="invalid_intersections")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invalid: {self.name}"
