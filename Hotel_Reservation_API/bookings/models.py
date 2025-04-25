from django.db import models
from accounts.models import User
# from hotels.models import Room
from django.conf import settings
from django.utils import timezone
# from hotels.models import Room
# from hotels.models import Hotel


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    hotel = models.ForeignKey("hotels.Hotel", on_delete=models.CASCADE, related_name="bookings", null=True, blank=True)
    room = models.ForeignKey("hotels.Room", on_delete=models.CASCADE, related_name="bookings")
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk: 
            days = (self.check_out - self.check_in).days
            self.total_price = self.room.price_per_night * days
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.id} - {self.user.username}"
    class Meta():
        db_table = "booking"


    