from django.db import models
from accounts.models import User
# from hotels.models import Room
from django.conf import settings
from django.utils import timezone
# # from hotels.models import Room
# # from hotels.models import Hotel


# class Booking(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('confirmed', 'Confirmed'),
#     ]
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
#     hotel = models.ForeignKey("hotels.Hotel", on_delete=models.CASCADE, related_name="bookings", null=True, blank=True)
#     room = models.ForeignKey("hotels.Room", on_delete=models.CASCADE, related_name="bookings")
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)
   
#     def save(self, *args, **kwargs):
#         if not self.pk: 
#             days = (self.check_out - self.check_in).days
#             self.total_price = self.room.price_per_night * days
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"Booking {self.id} - {self.user.username}"
#     class Meta():
#         db_table = "booking"

# class BookingCart(models.Model):
#     booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="cart")
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     created_at = models.DateTimeField(auto_now_add=True)
#     check_in = models.DateField(dafult=timezone.now)
#     days = models.IntegerField()
#     check_out = models.DateField()
#     def save(self, *args, **kwargs):
#         if not self.pk: 
#             days = (self.check_out - self.check_in).days
#             self.total_price = self.room.price_per_night * days
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"Booking Cart {self.id} - {self.user.username}"


from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    hotel = models.ForeignKey("hotels.Hotel", on_delete=models.CASCADE, related_name="bookings", null=True, blank=True)
    room = models.ForeignKey("hotels.Room", on_delete=models.CASCADE, related_name="bookings")
    check_in = models.DateField(default=timezone.now)
    check_out = models.DateField()
    days = models.IntegerField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if self.days and self.check_in:
            self.check_out = self.check_in + timezone.timedelta(days=self.days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.id} - {self.user.username}"

    class Meta:
        db_table = "booking"

class BookingCart(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="cart")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.booking:
            self.total_price = self.booking.total_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking Cart {self.id} - {self.booking.user.username}"
