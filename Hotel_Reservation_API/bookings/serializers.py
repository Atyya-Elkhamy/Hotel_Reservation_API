
from rest_framework import serializers
from .models import Booking, BookingCartItem, BookingCartSummary
from hotels.models import Hotel, RoomType
from hotels.serializers import *
from django.contrib.auth import get_user_model

User = get_user_model()

class BookingCartItemSerializer(serializers.ModelSerializer):
    room_type = RoomTypeSerializer(read_only=True)
    room_type_id = serializers.PrimaryKeyRelatedField(
        queryset=RoomType.objects.all(), source='room_type', write_only=True
    )
    class Meta:
        model = BookingCartItem
        fields = ['id', 'room_type', 'room_type_id', 'quantity']

from rest_framework import serializers
from .models import Booking, BookingCartItem, BookingCartSummary
from hotels.models import Room, RoomType, Hotel
from django.contrib.auth import get_user_model

User = get_user_model()

class BookingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    hotel = serializers.PrimaryKeyRelatedField(queryset=Hotel.objects.all())
    item_inputs = BookingCartItemSerializer(many=True)

    class Meta:
        model = Booking
        fields = ['user', 'hotel', 'check_in', 'days', 'item_inputs']

    def create(self, validated_data):
        item_data = validated_data.pop('item_inputs', [])
        booking = Booking.objects.create(**validated_data)

        total = 0
        print("the total is == ",total)
        for item in item_data:
            if 'room_type' not in item or 'quantity' not in item:
                raise serializers.ValidationError("Missing 'room_type' or 'quantity' in one of the items.")

            # Check if 'room_type_id' and 'quantity' exist in the item
            room_type = item['room_type']
            quantity = item['quantity']
            print("rooooom id is   ==== ",room_type)
            print("the quantity is   === ", quantity)
            print(room_type)
            if room_type.hotel != booking.hotel:
                raise serializers.ValidationError(f"Room type {room_type.room_type} does not belong to this hotel.")
            print("step oneeeeee ")
            room = Room.objects.filter(room_type=room_type, hotel=booking.hotel).first()
            print("step twooooooo")
            if not room:
                raise serializers.ValidationError(f"No room found for room type {room_type.room_type} in this hotel.")
            BookingCartItem.objects.create(booking=booking, room_type=room_type, quantity=quantity)
            print("step threeeeeeee ")
            total += room.price_per_night * quantity
            print("the total is now == ", total)

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

