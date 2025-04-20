from rest_framework import serializers
from .models import Booking
from datetime import timedelta

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['total_price']

    def validate(self, data):
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        room = data.get('room')

        if not room:
            raise serializers.ValidationError("Room must be specified.")

        if self.instance:
            if self.instance and self.instance.status in ['confirmed', 'cancelled']:
                raise serializers.ValidationError("You cannot edit a confirmed booking.")

        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError("Check-out must be after check-in.")
            num_nights = (check_out - check_in).days
            data['total_price'] = num_nights * room.price_per_night

        if check_in and check_out:
            existing_bookings = Booking.objects.filter(room=room)
            if self.instance:
                existing_bookings = existing_bookings.exclude(pk=self.instance.pk)

            for booking in existing_bookings:
                if booking.status == 'confirmed':
                    if check_in < booking.check_out and check_out > booking.check_in:
                        raise serializers.ValidationError(f"Room '{room}' is already booked from {booking.check_in} to {booking.check_out}.")



        if self.instance.status == 'confirmed':
            for booking in existing_bookings:
                if check_in < booking.check_out and check_out > booking.check_in:
                    raise serializers.ValidationError(f"Room {room} is already booked for the selected dates.")

        return data
