from rest_framework import serializers
from .models import Booking
from datetime import datetime
from datetime import date

from hotels.serializers import RoomSerializer , HotelSerializer

class BookingSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)
    hotel = HotelSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    total_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    has_conflict = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'

    def get_has_conflict(self, obj):
        if obj.status != 'pending':
            return False

        overlapping = Booking.objects.filter(
            room=obj.room,
            status='confirmed',
            check_in__lt=obj.check_out,
            check_out__gt=obj.check_in
        ).exclude(pk=obj.pk)

        return overlapping.exists()

    def validate(self, data):
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        room = data.get('room')
        status = data.get('status')
        today = date.today()

        if not room:
            raise serializers.ValidationError("Room must be specified.")

        if self.instance and self.instance.status == 'confirmed':
            raise serializers.ValidationError("You cannot edit a confirmed booking.")

        if check_in and check_out:
            # Check: dates must not be in the past
            if check_in < today:
                raise serializers.ValidationError({"check_in": "Check-in date cannot be in the past."})
            if check_out < today:
                raise serializers.ValidationError({"check_out": "Check-out date cannot be in the past."})

            # Check: checkout must be after check-in
            if check_out <= check_in:
                raise serializers.ValidationError({"check_out": "Check-out must be after check-in."})

            if status == 'confirmed' and self.instance.status != 'confirmed':
                existing_bookings = Booking.objects.filter(
                    room=room,
                    status='confirmed',
                    check_in__lt=check_out,
                    check_out__gt=check_in
                ).exclude(pk=self.instance.pk)

                if existing_bookings.exists():
                    raise serializers.ValidationError("The room is already confirmed for the selected dates.")

            # Check: overlapping bookings
            existing_bookings = Booking.objects.filter(room=room, status='confirmed')
            if self.instance:
                existing_bookings = existing_bookings.exclude(pk=self.instance.pk)

            for booking in existing_bookings:
                if check_in < booking.check_out and check_out > booking.check_in:
                    raise serializers.ValidationError({
                        'non_field_errors': [
                            f"Room '{room}' is already booked from {booking.check_in} to {booking.check_out}."
                        ]
                    })

        return data

    def create(self, validated_data):
        check_in = validated_data['check_in']
        check_out = validated_data['check_out']
        room = validated_data['room']

        # Perform the same validation for overlapping bookings here
        if check_in and check_out:
            existing_bookings = Booking.objects.filter(room=room, status='confirmed')

            # Check for overlapping bookings
            for booking in existing_bookings:
                if check_in < booking.check_out and check_out > booking.check_in:
                    raise serializers.ValidationError({
                        'non_field_errors': [
                            f"Room '{room}' is already booked from {booking.check_in} to {booking.check_out}."
                        ]
                    })

        # Convert string dates to datetime if necessary
        if isinstance(check_in, str):
            check_in = datetime.strptime(check_in, "%Y-%m-%d").date()
        if isinstance(check_out, str):
            check_out = datetime.strptime(check_out, "%Y-%m-%d").date()

        num_nights = (check_out - check_in).days
        validated_data['total_price'] = num_nights * room.price_per_night

        return super().create(validated_data)

