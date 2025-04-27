from django.db import models
from accounts.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid  
from datetime import datetime
from django.utils import timezone
from django.utils.timezone import now
from bookings.models import Booking
from uuid import uuid4
# from django.contrib.gis.db import models as geomodels

class Hotel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hotels", null=True)
    name = models.CharField(max_length=255 , unique=True)
    description = models.TextField(blank=True, null=True ,max_length=500)
    address = models.TextField(max_length=200)
    phone = models.CharField(max_length=20, unique=True , default='')
    stars = models.PositiveIntegerField(validators=[MinValueValidator(3), MaxValueValidator(7)],  null= True)
    email = models.EmailField(unique=True ,max_length=100 , null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    price_range = models.CharField(max_length=50, blank=True, null=True)
    # latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    @property
    def rooms(self):
        return self.rooms_set.all()
    def __str__(self):
        return self.name
    class Meta():
        db_table = "hotel"

class HotelImage(models.Model):
    def Hotel_image_path(instance,filename):
        ext = filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        return f'hotel_images/{datetime.now().strftime("%y/%m/%d")}/{uuid4()}.{filename.split(".")[-1]}'
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=Hotel_image_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.hotel.name}"

    class Meta:
        db_table = "hotel_image"

# Room Model
class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="rooms")
    room_type = models.ForeignKey('Roomtype', on_delete=models.CASCADE, related_name="rooms")
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    total_rooms = models.PositiveIntegerField()
    available_rooms = models.PositiveIntegerField(null=True,default=0)
    amenities = models.TextField(max_length=500 , null=True) 

    def save(self, *args, **kwargs):
        if self.pk is None:  # Check if the object is being created
            self.available_rooms = self.total_rooms
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.hotel.name} - {self.room_type}"
    class Meta():
        db_table = "room"
#room type model
class RoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="roomtype")
    room_type = models.CharField(max_length=100 , unique=True)
 
    def __str__(self):
        return f"{self.hotel.name} - {self.room_type}"

    class Meta:
        db_table = "room_type"

class RoomImage(models.Model):
    def Room_image_path(instance,filename):
        ext = filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        return f'room_images/{datetime.now().strftime("%y/%m/%d")}/{uuid4()}.{filename.split(".")[-1]}'

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=Room_image_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.room.room_type}"

    class Meta:
        db_table = "room_image"
# class HotelLocation(geomodels.Model):