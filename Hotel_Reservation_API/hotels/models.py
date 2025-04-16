from django.db import models
from accounts.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Hotel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hotels")
    name = models.CharField(max_length=255 , unique=True)
    description = models.TextField(blank=True, null=True ,max_length=500)
    location = models.CharField(max_length=255)
    address = models.TextField(max_length=200)
    phone = models.CharField(max_length=20, unique=True)
    stars = models.PositiveIntegerField(validators=[MinValueValidator(3), MaxValueValidator(7)])
    email = models.EmailField(unique=True ,max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    class Meta():
        db_table = "hotel"

class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="hotel_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.hotel.name}"

    class Meta:
        db_table = "hotel_image"

# Room Model
class Room(models.Model):
    ROOM_TYPES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite'),
    ]
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="rooms")
    room_type = models.CharField(max_length=100, choices=ROOM_TYPES)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    total_rooms = models.PositiveIntegerField()
    available_rooms = models.PositiveIntegerField()
    amenities = models.TextField(max_length=500)  

    def __str__(self):
        return f"{self.hotel.name} - {self.room_type}"
    class Meta():
        db_table = "room"


