from django.urls import path
from .views import *

urlpatterns = [
    path('create/', HotelListView.as_view(), name='hotel-list'),
    path('update/<int:pk>/', HotelUpdateView.as_view(), name='hotel-update'),
    path('hoteldetail/<int:pk>/', HotelDetailView.as_view(), name='hotel-detail'),
    path('hotelupdate/<int:pk>/', HotelUpdateView.as_view(), name='hotel-update'),
    path('hoteldelete/<int:pk>/', HotelDeleteView.as_view(), name='hotel-delete'),
    path('roomcreate/', RoomCreateView.as_view(), name='room-create'),
    path('roomupdate/<int:pk>/', RoomUpdateView.as_view(), name='room-update'),
    path('roomdelete/<int:pk>/', RoomDeleteView.as_view(), name='room-delete'),
]