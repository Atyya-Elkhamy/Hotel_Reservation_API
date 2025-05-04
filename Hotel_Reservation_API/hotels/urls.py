from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('', HotelListView.as_view(), name='hotel-list'),
    path('create/', HotelListView.as_view(), name='hotel-create'),
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
    path('rooms/<int:hotel_id>/', RoomsByHotelView.as_view(), name='rooms-by-hotel'),
    path("details/ownerhoteldetails/",OwnerHotelListView.as_view(), name='owner-hoteldetails'),
   # Hotel Images
    path("createimage/", HotelImageCreateView.as_view(), name="hotel-image-create"),
    path("listimages/", HotelImageListView.as_view(), name="hotel-image-list"),
    path("listimages/<int:pk>/", HotelImageListView.as_view(), name="hotel-image-list-pk"),
    path("updateimage/<int:pk>/", HotelImageUpdateView.as_view(), name="hotel-image-update"),
    path("deleteimage/<int:pk>/", HotelImageDeleteView.as_view(), name="hotel-image-delete"),
    path("roomcreateimage/", RoomImageCreateView.as_view(), name="room-image-create"),
    path("roomlistimages/<int:pk>/", RoomImageListView.as_view(), name="room-image-list-pk"),
    path("roomupdateimage/<int:pk>/", RoomImageUpdateView.as_view(), name="room-image-update"),
    path("roomdeleteimage/<int:pk>/", RoomImageDeleteView.as_view(), name="room-image-delete"),
    path ("roomcreatetype/", RoomTypeView.as_view(), name="room-type-create"),
    path("hotelroometype/<int:hotel_id>/", HotelsRoomTypeView.as_view(), name="room-type-by-hotel"),
]       