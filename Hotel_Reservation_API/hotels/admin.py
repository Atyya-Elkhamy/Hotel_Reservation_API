from django.contrib import admin
 
from .models import Hotel , HotelImage , Room ,RoomImage


admin.site.register(Hotel)
admin.site.register(HotelImage)
admin.site.register(Room)
admin.site.register(RoomImage)