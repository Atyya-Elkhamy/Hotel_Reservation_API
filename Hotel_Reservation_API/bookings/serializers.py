from rest_framework import serializers
from .models import Booking
from datetime import timedelta
from .models import Payment
from hotels.serializers import RoomSerializer , HotelSerializer


class BookingSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)
    hotel = HotelSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = "__all__"

    def validate(self, data):
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        room = data.get('room')

        if not room:
            raise serializers.ValidationError("Room must be specified.")

        if self.instance:
            if self.instance.status in ['confirmed', 'cancelled']:
                raise serializers.ValidationError("You cannot edit a confirmed or cancelled booking.")

        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError("Check-out must be after check-in.")

        # Overlapping bookings check
        if check_in and check_out:
            existing_bookings = Booking.objects.filter(room=room, status='confirmed')
            if self.instance:
                existing_bookings = existing_bookings.exclude(pk=self.instance.pk)

            for booking in existing_bookings:
                if check_in < booking.check_out and check_out > booking.check_in:
                    raise serializers.ValidationError(
                        f"Room '{room}' is already booked from {booking.check_in} to {booking.check_out}."
                    )

        return data

    def create(self, validated_data):
        check_in = validated_data['check_in']
        check_out = validated_data['check_out']
        room = validated_data['room']

        num_nights = (check_out - check_in).days
        validated_data['total_price'] = num_nights * room.price_per_night

        return super().create(validated_data)
