from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class SendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    message = serializers.CharField()