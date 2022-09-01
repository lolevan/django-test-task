from django.urls import path

from .views import *


app_name = 'products'
urlpatterns = [
    path('users/', RegistrationAPIView.as_view(), name='users'),
    path('users/login/', LoginAPIView.as_view(), name='login'),
]
