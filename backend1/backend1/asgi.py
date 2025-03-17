import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.layers import get_channel_layer
import polygons.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend1.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(polygons.routing.websocket_urlpatterns),
})

channel_layer = get_channel_layer()
