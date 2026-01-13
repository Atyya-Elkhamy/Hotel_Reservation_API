from rest_framework import serializers
from .models import Payment, PaymentSettings
import re
from hotels.serializers import RoomSerializer,HotelSerializer
from bookings.serializers import BookingSerializer

class ClientInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField()
    city = serializers.CharField(max_length=100)
    region = serializers.CharField(max_length=100)
    payment_type = serializers.ChoiceField(choices=['cash', 'online'])
    
    def validate_phone(self, value):
        pattern = r'^(011|012|015|010)\d{8}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Phone number must be 11 digits and start with 011, 012, 015, or 010.")
        return value
    
    def validate_email(self, value):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise serializers.ValidationError("Invalid email format.")
        return value
    
class PaymentMethodSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=Payment.PaymentMethodChoice.choices)

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


class PaymentSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSettings
        fields = ['allow_card_payment', 'allow_paypal', 'allow_bank_transfer', 'deposit_percentage']

# class PaymentSettingsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PaymentSettings
#         fields = "__all__"


