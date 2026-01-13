from rest_framework import serializers
from .models import Hotel, Room, HotelImage , RoomType , RoomImage
import re
from accounts.serializers import UserSerializer
from accounts.models import User

class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = "__all__"

class RoomSerializerFetch(serializers.ModelSerializer):
    room_type = RoomTypeSerializer()  
    class Meta:
        model = Room
        fields = "__all__"

class RoomSerializer(serializers.ModelSerializer):
    room_type = serializers.PrimaryKeyRelatedField(queryset=RoomType.objects.all())
    class Meta:
        model = Room
        exclude = ['available_rooms']
    def validate(self, attrs):
        total_rooms = attrs.get('total_rooms')
        available_rooms = attrs.get('available_rooms')
        price_per_night = attrs.get('price_per_night')
        hotel = attrs.get('hotel')
        room_type = attrs.get('room_type')
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
        if hotel and room_type and room_type.hotel != hotel:
            errors['room_type'] = "Selected room type does not belong to the selected hotel"
        if errors:
            raise serializers.ValidationError(errors)
        return attrs
    def create(self, validated_data):
        validated_data['available_rooms'] = validated_data.get('total_rooms', 0)
        return super().create(validated_data)

class HotelSerializer(serializers.ModelSerializer):
    rooms = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    class Meta:
        model = Hotel
        fields = '__all__'
    def get_rooms(self, obj):
        from .serializers import RoomSerializer 
        rooms = Room.objects.filter(hotel=obj)
        return RoomSerializer(rooms, many=True).data
    def get_image(self, obj):
        from .serializers import HotelImageSerializer 
        images = HotelImage.objects.filter(hotel=obj)
        return HotelImageSerializer(images, many=True).data
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
        if not re.match(r"^[a-zA-Z\s']+$", name):
            raise serializers.ValidationError({"name": "Name must contain only letters and spaces"})
        return attrs
    def create(self, validated_data):
        return super().create(validated_data)

class HotelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelImage
        exclude = ['hotel']
    def validate(self, attrs):
        image = attrs.get('image')
        if not image:
            raise serializers.ValidationError({"image": "Image is required"})
        if not image.name.endswith(('.png', '.jpg', '.jpeg')):
            raise serializers.ValidationError({"image": "Image must be a PNG, JPG, or JPEG file"})
        return attrs
    def create(self, validated_data):
        return super().create(validated_data)


class RoomImageSerializer(serializers.ModelSerializer):
    room = RoomSerializerFetch()
    hotel = HotelSerializer(read_only=True)
    class Meta:
        model = RoomImage
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
    
class RoomImageSerializerAdd(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    hotel = HotelSerializer(read_only=True)
    class Meta:
        model = RoomImage
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

class HotelSerializerCreate(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Hotel
        fields = '__all__'

    def get_rooms(self, obj):
        from .serializers import RoomSerializer 
        rooms = Room.objects.filter(hotel=obj)
        return RoomSerializer(rooms, many=True).data

    def get_image(self, obj):
        from .serializers import HotelImageSerializer 
        images = HotelImage.objects.filter(hotel=obj)
        return HotelImageSerializer(images, many=True).data

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
        if not re.match(r"^[a-zA-Z\s']+$", name):
            raise serializers.ValidationError({"name": "Name must contain only letters and spaces"})
        return attrs

    def create(self, validated_data):
        return super().create(validated_data)


