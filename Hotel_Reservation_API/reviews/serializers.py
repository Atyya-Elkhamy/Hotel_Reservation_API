from rest_framework import serializers
from .models import Review
from accounts.models import User
from hotels.models import Hotel

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class HotelSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = "__all__"

class ReviewSerializer(serializers.ModelSerializer):
    user_details = UserSimpleSerializer(source='user', read_only=True)
    hotel_details = HotelSimpleSerializer(source='hotel', read_only=True)

    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate(self, data):
        user = self.context['request'].user
        hotel = data.get('hotel')

        if not self.instance and Review.objects.filter(user=user, hotel=hotel).exists():
            raise serializers.ValidationError("You have already reviewed this hotel.")

        return data