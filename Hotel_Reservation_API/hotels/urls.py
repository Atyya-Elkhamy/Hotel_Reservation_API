from django.urls import path
from .views import *

urlpatterns = [
    path('create/', HotelListView.as_view(), name='hotel-list'),
    path('update/<int:pk>/', HotelUpdateView.as_view(), name='hotel-update'),
    path('detail/<int:pk>/', HotelDetailView.as_view(), name='hotel-detail'),
    path('delete/<int:pk>/', HotelDeleteView.as_view(), name='hotel-delete'),
    path('hotelfilter/<int:stars>/', HotelFilterByStarsView.as_view(), name='hotel-filter'),
    path('roomcreate/', RoomCreateView.as_view(), name='room-create'),
    path('roomlist/', RoomListView.as_view(), name='room-list'),
    path('roomupdate/<int:pk>/', RoomUpdateView.as_view(), name='room-update'),
    path('roomdelete/<int:pk>/', RoomDeleteView.as_view(), name='room-delete'),
    path('roomdetail/<int:pk>/', RoomDetailView.as_view(), name='room-detail'),
    path('roomfilter/<str:room_type>/', RoomFilterByTypeView.as_view(), name='room-filter'),
    path("createimage/", HotelImageCreateView.as_view(), name="hotel-image-create"),
    path("listimages/", HotelImageListView.as_view(), name="hotel-image-list"),
    path("updateimage/<int:pk>/", HotelImageUpdateView.as_view(), name="hotel-image-update"),
    path("deleteimage/<int:pk>/", HotelImageDeleteView.as_view(), name="hotel-image-delete"),

]