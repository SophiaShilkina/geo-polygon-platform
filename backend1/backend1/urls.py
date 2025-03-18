from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from polygons.views import PolygonViewSet, InvalidPolygonViewSet
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version='v1',
        description="API documentation",
    ),
    public=True,
)


router = DefaultRouter()
router.register(r'polygons', PolygonViewSet, basename='polygon')
router.register(r'invalid-polygons', InvalidPolygonViewSet, basename='invalid-polygon')


urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('swagger.json', schema_view.without_ui(cache_timeout=0)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
    path('api/', include('polygons.urls')),
]
