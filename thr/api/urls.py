from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import registration_view, logout_view

urlpatterns = [
    path('register', registration_view, name='register_api'),
    path('login', obtain_auth_token, name='login_api'),
    path('logout', logout_view, name='logout_api'),
]
