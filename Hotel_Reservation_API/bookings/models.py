from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    hotel = models.ForeignKey("hotels.Hotel", on_delete=models.CASCADE, related_name="bookings", null=True, blank=True)
    check_in = models.DateField(default=timezone.now)
    check_out = models.DateField()
    days = models.IntegerField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        from hotels.models import Room 
        if self.days and self.check_in:
            self.check_out = self.check_in + timezone.timedelta(days=self.days)
        total = 0
        print("the total is === ", total)
        if self.pk:  
            for item in self.items.all():
                print("the item is === ", item)
                room = Room.objects.filter(hotel=self.hotel, room_type=item.room_type).first()
                if room:
                    total += item.quantity * room.price_per_night
            total *= self.days or 1
            self.total_price = total
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Booking {self.id} - {self.user.username}"

    class Meta:
        db_table = "booking"


class BookingCartItem(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="items")
    room_type = models.ForeignKey("hotels.RoomType", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def clean(self):
        if self.room_type.hotel != self.booking.hotel:
            raise ValidationError("All room types in the booking must be from the same hotel.")

    def __str__(self):
        return f"{self.quantity} x {self.room_type.room_type} for Booking {self.booking.id}"
    class Meta:
        db_table = "booking_cart_item"
        unique_together = ('booking', 'room_type')


class BookingCartSummary(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="cart_summary")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        from hotels.models import Room
        total = 0
        if self.booking:
            for item in self.booking.items.all():
                room = Room.objects.filter(hotel=self.booking.hotel, room_type=item.room_type).first()
                if room:
                    total += item.quantity * room.price_per_night
                else:
                    print(f"⚠️ Room not found for {item.room_type}")
            total *= self.booking.days or 1
        self.total_price = total
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking Cart Summary {self.id} - {self.booking.user.username}"
