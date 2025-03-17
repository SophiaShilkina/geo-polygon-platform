from django.urls import path
from polygons.views import PolygonCheckView


urlpatterns = [
    path('check/', PolygonCheckView.as_view(), name='polygon-check'),
]
