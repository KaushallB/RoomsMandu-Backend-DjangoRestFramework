from django.urls import path

from . import api

urlpatterns = [
    path('',api.properties_list, name='api_properties_list'),
    path('create/', api.create_property, name='api_create_property'),
    path('inquiries/', api.get_my_inquiries, name='api_get_my_inquiries'),
    path('<uuid:pk>/',api.properties_details, name='api_properties_detail'),
    path('<uuid:pk>/book/',api.book_property, name='api_book_properties'),
    path('<uuid:pk>/toggle_favourites/', api.toggle_favourite, name='api_toggle_favourite'),
    path('<uuid:pk>/delete/', api.delete_property, name='api_delete_property'),
    path('<uuid:pk>/toggle_availability/', api.toggle_availability, name='api_toggle_availability'),
    
    # Video Call URLs
    path('<uuid:pk>/schedule-call/', api.schedule_video_call, name='api_schedule_video_call'),
    path('video-calls/', api.get_my_video_calls, name='api_get_my_video_calls'),
    path('video-calls/<uuid:pk>/', api.get_video_call, name='api_get_video_call'),
    path('video-calls/<uuid:pk>/confirm/', api.confirm_video_call, name='api_confirm_video_call'),
]

