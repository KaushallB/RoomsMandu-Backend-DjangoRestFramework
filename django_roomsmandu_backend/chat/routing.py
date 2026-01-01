from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
    path('ws/calls/<str:user_id>/', consumers.CallConsumer.as_asgi()),
    path('ws/notifications/<str:user_id>/', consumers.NotificationConsumer.as_asgi()),
]