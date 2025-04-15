from django.urls import path
from .views import *

urlpatterns = [
    path('create/', HotelListView.as_view(), name='hotel-list'),
    path('update/<int:pk>/', HotelUpdateView.as_view(), name='hotel-update'),
    # path('rooms/', RoomListView.as_view(), name='room-list'),
    # path('rooms/<int:pk>/', RoomUpdateView.as_view(), name='room-update'),
]