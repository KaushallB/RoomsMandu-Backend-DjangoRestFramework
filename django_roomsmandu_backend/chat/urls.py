from django.urls import path

from . import api

urlpatterns = [
    path('',api.conversation_list, name='api_conversations'),
    
    path('<uuid:pk>/', api.convo_detail, name='api_conversations_detail'),
    path('start/<uuid:user_id>/', api.convo_start, name='api_conversations_start'),
    path('<uuid:conversation_id>/start-call/', api.start_instant_call, name='api_start_instant_call'),
]
