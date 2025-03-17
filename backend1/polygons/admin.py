from django.contrib import admin
from .models import Polygon, PolygonUserAssignment, InvalidPolygon


@admin.register(Polygon)
class PolygonAdmin(admin.ModelAdmin):
    list_display = ("name", "crosses_antimeridian")

@admin.register(PolygonUserAssignment)
class PolygonUserAssignmentAdmin(admin.ModelAdmin):
    list_display = ("polygon", "user", "assigned_at", "assigned_by")

@admin.register(InvalidPolygon)
class InvalidPolygonAdmin(admin.ModelAdmin):
    list_display = ("name", "reason", "created_at")
