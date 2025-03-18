from django.urls import path
from .views import PolygonViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'polygons', PolygonViewSet)

urlpatterns = router.urls
