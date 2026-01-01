from django.urls import path

from dj_rest_auth.jwt_auth import get_refresh_view
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from rest_framework_simplejwt.views import TokenVerifyView
from . import api

urlpatterns = [
    path('register/', RegisterView.as_view(), name='rest_register'),
    path('login/', LoginView.as_view(), name='rest_login'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('me/', UserDetailsView.as_view(), name='rest_user_details'), 
    path('profile/', api.my_profile, name='api_my_profile'),
    path('<uuid:pk>/', api.landlord_detail, name='api_landlord_details'),
    path('myreservations/', api.reservation_list, name='api_reservation_list'),
    path('token/refresh/', get_refresh_view().as_view(), name='token_refresh')
]
