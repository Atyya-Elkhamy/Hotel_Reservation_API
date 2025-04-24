from django.contrib import admin
<<<<<<< HEAD
from .models import Hotel

admin.site.register(Hotel)
=======
 
from .models import Hotel , HotelImage , Room ,RoomImage


admin.site.register(Hotel)
admin.site.register(HotelImage)
admin.site.register(Room)
admin.site.register(RoomImage)
>>>>>>> origin/bookingCycle
