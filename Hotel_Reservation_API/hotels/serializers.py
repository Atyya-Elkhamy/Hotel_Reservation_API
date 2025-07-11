from rest_framework import serializers
from .models import Hotel, Room , HotelImage
import re

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'

    def validate(self, attrs):
        stars = attrs.get('stars')
        phone = attrs.get('phone')
        email = attrs.get('email')
        name = attrs.get('name')

        if not (3 <= stars <= 7):
            raise serializers.ValidationError({"stars": "Stars must be between 3 and 7"})

        if not (phone and phone.startswith(('010', '012', '011', '015')) and len(phone) == 11 and phone.isdigit()):
            raise serializers.ValidationError({"phone": "Phone number must be 11 digits and start with 010, 012, 011, or 015"})

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise serializers.ValidationError({"email": "Invalid email format"})

        if not name.isalpha():
            raise serializers.ValidationError({"name": "Name must contain only letters"})

        return attrs

    def create(self, validated_data):
        return super().create(validated_data)


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
    def validate(self, attrs):
        total_rooms = attrs.get('total_rooms')
        available_rooms = attrs.get('available_rooms')
        price_per_night = attrs.get('price_per_night')

        errors = {}

        if total_rooms is not None and total_rooms < 1:
            errors['total_rooms'] = "Total rooms must be at least 1"

        if available_rooms is not None:
            if available_rooms < 0:
                errors['available_rooms'] = "Available rooms cannot be negative"
            elif total_rooms is not None and available_rooms > total_rooms:
                errors['available_rooms'] = "Available rooms cannot exceed total rooms"

        if price_per_night is not None and price_per_night <= 0:
            errors['price_per_night'] = "Price per night must be greater than 0"

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        return super().create(validated_data)
    

class HotelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelImage
        fields = '__all__'
   
    def validate(self, attrs):
        image = attrs.get('image')
        if not image:
            raise serializers.ValidationError({"image": "Image is required"})
        if not image.name.endswith(('.png', '.jpg', '.jpeg')):
            raise serializers.ValidationError({"image": "Image must be a PNG, JPG, or JPEG file"})
        return attrs
    def create(self, validated_data):
        return super().create(validated_data)