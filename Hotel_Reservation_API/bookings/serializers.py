
from rest_framework import serializers
from .models import Booking, BookingCartItem, BookingCartSummary
from hotels.models import Hotel, RoomType ,Room
from hotels.serializers import *
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date
from django.db import IntegrityError
User = get_user_model()

class BookingCartItemSerializer(serializers.ModelSerializer):
    room_type = RoomTypeSerializer(read_only=True)
    room_type_id = serializers.PrimaryKeyRelatedField(
        queryset=RoomType.objects.all(), source='room_type', write_only=True
    )
    class Meta:
        model = BookingCartItem
        fields = ['id', 'room_type', 'room_type_id', 'quantity']


# class BookingSerializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
#     hotel = serializers.PrimaryKeyRelatedField(queryset=Hotel.objects.all())
#     item_inputs = BookingCartItemSerializer(many=True)
#     class Meta:
#         model = Booking
#         fields = ['user', 'hotel', 'check_in', 'days', 'item_inputs']

#     def validate_check_in(self, value):
#         today = date.today()
#         if value < today:
#             raise serializers.ValidationError("Check-in date must be at least 1 days from today.")
#         return value

#     def create(self, validated_data):
#         item_data = validated_data.pop('item_inputs', [])
#         booking = Booking.objects.create(**validated_data)
#         total = 0
#         for item in item_data:
#             if 'room_type' not in item or 'quantity' not in item:
#                 raise serializers.ValidationError({"room_type":"Missing 'room_type' or 'quantity' in one of the items."})
#             room_type = item['room_type']
#             quantity = item['quantity']
#             if room_type.hotel != booking.hotel:
#                 raise serializers.ValidationError({"room_type":f"Room type {room_type.room_type} does not belong to this hotel."})
#             room = Room.objects.filter(room_type=room_type, hotel=booking.hotel).first()
#             if not room:
#                 raise serializers.ValidationError({"room_type":f"No room found for room type {room_type.room_type} in this hotel."})
#             if quantity > room.available_rooms:
#                 raise serializers.ValidationError({"quantity":
#                     f"Requested quantity ({quantity}) exceeds available rooms ({room.available_rooms}) "
#                     f"for room type {room_type.room_type}."}
#                 )
#             BookingCartItem.objects.create(booking=booking, room_type=room_type, quantity=quantity)
#             total += room.price_per_night * quantity
#         if booking.days:
#             total *= booking.days
#         booking.total_price = total
#         booking.save()
#         BookingCartSummary.objects.create(booking=booking)
#         return booking
class BookingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    hotel = serializers.PrimaryKeyRelatedField(queryset=Hotel.objects.all())
    item_inputs = BookingCartItemSerializer(many=True)

    class Meta:
        model = Booking
        fields = ['user', 'hotel', 'check_in', 'days', 'item_inputs']

    def validate_check_in(self, value):
        today = date.today()
        if value < today:
            raise serializers.ValidationError("Check-in date must be at least 1 day from today.")
        return value

    def validate(self, data):
        # Check for duplicate room_type entries
        room_type_ids = [item['room_type'].id for item in data.get('item_inputs', []) if 'room_type' in item]
        if len(room_type_ids) != len(set(room_type_ids)):
            raise serializers.ValidationError({
                "item_inputs": "Duplicate room types are not allowed. Please only include each room type once."
            })
        return data

    def create(self, validated_data):
        item_data = validated_data.pop('item_inputs', [])
        booking = Booking.objects.create(**validated_data)
        total = 0

        for item in item_data:
            if 'room_type' not in item or 'quantity' not in item:
                raise serializers.ValidationError({"room_type": "Missing 'room_type' or 'quantity' in one of the items."})
            
            room_type = item['room_type']
            quantity = item['quantity']

            if room_type.hotel != booking.hotel:
                raise serializers.ValidationError({
                    "room_type_id": f"Room type {room_type.room_type} does not belong to this hotel."
                })

            room = Room.objects.filter(room_type=room_type, hotel=booking.hotel).first()
            if not room:
                raise serializers.ValidationError({
                    "room_type_id": f"No room found for room type {room_type.room_type} in this hotel."
                })

            if quantity > room.available_rooms:
                raise serializers.ValidationError({
                    "quantity": f"Requested quantity ({quantity}) exceeds available rooms ({room.available_rooms}) "
                                f"for room type {room_type.room_type}."
                })

            try:
                BookingCartItem.objects.create(booking=booking, room_type=room_type, quantity=quantity)
            except IntegrityError:
                raise serializers.ValidationError({
                    "room_type_id": f"Duplicate entry detected for room type {room_type.room_type}."
                })

            total += room.price_per_night * quantity

        if booking.days:
            total *= booking.days

        booking.total_price = total
        booking.save()

        BookingCartSummary.objects.create(booking=booking)
        return booking

class BookingCartSummarySerializer(serializers.ModelSerializer):
    booking = serializers.PrimaryKeyRelatedField(queryset=Booking.objects.all())
    class Meta:
        model = BookingCartSummary
        fields = "__all__"
        
class BookingPaymentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    hotel = HotelSerializer(read_only=True)
    items = BookingCartItemSerializer(many=True)
    summary = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = "__all__"
    def get_summary(self, obj):
        summary = getattr(obj, 'cart_summary', None)
        return {
            "total_price": summary.total_price if summary else 0,
            "created_at": summary.created_at if summary else None
        }
        return super().create(validated_data)

class ListBookingsSerializer(serializers.ModelSerializer):
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    client_name = serializers.CharField(source='user.username', read_only=True)
    client_email = serializers.EmailField(source='user.email', read_only=True)
    hotel_address = serializers.CharField(source='hotel.address', read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    check_in = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    check_out = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    hotel_image = serializers.ImageField(source='hotel.images.first.image', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id','user','client_name','client_email', 'hotel', 'hotel_name', 'check_in', 'check_out',
            'total_price', 'status', 'created_at','hotel_image','hotel_address'
        ]

class CustomHotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'owner','address']  

class CustomBookingCartItemSerializer(serializers.ModelSerializer):
    room_type = serializers.StringRelatedField()
    
    class Meta:
        model = BookingCartItem
        fields = ['id', 'room_type', 'quantity']

class CustomBookingPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingCartSummary  
        fields = ['total_price', 'created_at']

class CustomBookingSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='user.username', read_only=True)
    client_email = serializers.EmailField(source='user.email', read_only=True)
    client_phone = serializers.CharField(source='user.phone', read_only=True)
    class Meta:
        model = Booking
        fields = ['id', 'client_name','client_email','client_phone', 'check_in', 'check_out', 'total_price', 'status', 'created_at']