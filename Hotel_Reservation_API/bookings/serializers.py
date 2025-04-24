from rest_framework import serializers
from .models import Booking
from datetime import datetime
from datetime import date

# class BookingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Booking
#         fields = '__all__'
#         read_only_fields = ['total_price']

#     def validate(self, data):
#         check_in = data.get('check_in')
#         check_out = data.get('check_out')
#         room = data.get('room')

#         if not room:
#             raise serializers.ValidationError("Room must be specified.")

#         if self.instance:
#             if self.instance.status in ['confirmed', 'cancelled']:
#                 raise serializers.ValidationError("You cannot edit a confirmed booking.")

#         if check_in and check_out:
#             if check_out <= check_in:
#                 raise serializers.ValidationError("Check-out must be after check-in.")
#             num_nights = (check_out - check_in).days
#             data['total_price'] = num_nights * room.price_per_night

#         if check_in and check_out:
#             existing_bookings = Booking.objects.filter(room=room)
#             if self.instance:
#                 existing_bookings = existing_bookings.exclude(pk=self.instance.pk)

#             for booking in existing_bookings:
#                 if booking.status == 'confirmed':
#                     if check_in < booking.check_out and check_out > booking.check_in:
#                         raise serializers.ValidationError(f"Room '{room}' is already booked from {booking.check_in} to {booking.check_out}.")



#         if self.instance.status == 'confirmed':
#             for booking in existing_bookings:
#                 if check_in < booking.check_out and check_out > booking.check_in:
#                     raise serializers.ValidationError(f"Room {room} is already booked for the selected dates.")

#         return data
        # def validate(self, data):
        #     check_in = data.get('check_in')
        #     check_out = data.get('check_out')
        #     room = data.get('room')

        #     if not room:
        #         raise serializers.ValidationError("Room must be specified.")

        #     # Prevent editing a confirmed or cancelled booking
        #     if self.instance:
        #         if self.instance.status in ['confirmed', 'cancelled']:
        #             raise serializers.ValidationError("You cannot edit a confirmed or cancelled booking.")

        #     # Validate check-in and check-out dates
        #     if check_in and check_out:
        #         if check_out <= check_in:
        #             raise serializers.ValidationError("Check-out must be after check-in.")

        #         # Calculate total price
        #         num_nights = (check_out - check_in).days
        #         data['total_price'] = num_nights * room.price_per_night

        #     # Check for overlapping bookings
        #     if check_in and check_out:
        #         existing_bookings = Booking.objects.filter(room=room, status='confirmed')

        #         if self.instance:
        #             existing_bookings = existing_bookings.exclude(pk=self.instance.pk)

        #         for booking in existing_bookings:
        #             if check_in < booking.check_out and check_out > booking.check_in:
        #                 raise serializers.ValidationError(
        #                     f"Room '{room}' is already booked from {booking.check_in} to {booking.check_out}."
        #                 )

        #     return data

class BookingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    total_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = Booking
        fields = '__all__'

    def validate(self, data):
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        room = data.get('room')
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

