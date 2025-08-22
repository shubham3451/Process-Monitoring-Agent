from django.urls import path
from . import ws_consumers

websocket_urlpatterns = [
    path("ws/hosts/<str:hostname>/", ws_consumers.HostConsumer.as_asgi()),
]
