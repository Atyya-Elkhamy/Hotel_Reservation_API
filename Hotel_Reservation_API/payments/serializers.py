from rest_framework import serializers
from .models import Payment
import re
from hotels.serializers import RoomSerializer,HotelSerializer
from bookings.serializers import BookingSerializer



class PaymentSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    hotel = HotelSerializer(read_only=True)
    class Meta:
        model = Payment
        fields = "__all__"
        exclude = ["transaction_id","amount","status","payment_date",]

    def validate(self, data):
        booking = data.get('booking')
        amount = data.get('amount')
        is_deposit = data.get('is_deposit')
        phone = data.get('phone')
        email = data.get('email')

        if booking and hasattr(booking, 'payment'):
            raise serializers.ValidationError({
                "booking": "This booking already has a payment."
            })
        if amount is not None and amount <= 0:
            raise serializers.ValidationError({
                "amount": "Amount must be greater than zero."
            })
        if phone:
            pattern = r'^(011|012|015|010)\d{8}$'
            if not re.match(pattern, phone):
                raise serializers.ValidationError({
                    "phone": "Phone number must be 11 digits and start with 011, 012, 015, or 010."
                })
            
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                raise serializers.ValidationError({
                    "email": "Invalid email format."
                })
    
        if is_deposit:
            total_price = booking.total_price if booking else None
            expected_deposit = Payment.calculate_deposit(total_price) if total_price else None
            if expected_deposit and amount != expected_deposit:
                raise serializers.ValidationError({
                    "amount": f"Deposit should be exactly {expected_deposit} for this booking."
                })

        return data


# class PaymentSettingsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PaymentSettings
#         fields = "__all__"


