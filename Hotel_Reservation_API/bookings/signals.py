# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from hotels.models import Room

@receiver(post_save, sender=Booking)
def update_available_rooms(sender, instance, created, **kwargs):
    if instance.status == 'confirmed':
        for item in instance.items.all():
            room = Room.objects.filter(hotel=instance.hotel, room_type=item.room_type).first()
            if room:
                if room.available_rooms >= item.quantity:
                    room.available_rooms -= item.quantity
                    room.save()
                else:
                    raise ValueError("Not enough available rooms.")
