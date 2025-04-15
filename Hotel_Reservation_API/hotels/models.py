from django.db import models
from accounts.models import User


# Create your models here.


class Hotel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hotels")
    name = models.CharField(max_length=255 , unique=True)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True, null=True ,unique=True)
    email = models.EmailField(blank=True, null=True,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    class Meta():
        db_table = "hotel"

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
    amenities = models.TextField(blank=True, null=True)  # Can be stored as JSON

    def __str__(self):
        return f"{self.hotel.name} - {self.room_type}"
    class Meta():
        db_table = "room"


