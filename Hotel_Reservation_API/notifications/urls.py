from django.urls import path
from .views import *

urlpatterns = [
    path('send-email/', send_test_email, name='send-email'),
]
