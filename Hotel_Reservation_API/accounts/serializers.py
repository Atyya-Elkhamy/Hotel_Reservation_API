from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
User = get_user_model()
import re
from .models import User

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'role', 'password', 'password2', 'confirmed']
        read_only_fields = ['id', 'confirmed']
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True}
        }

    def validate_username(self, value):
        if not re.match(r'^[A-Za-z]+$', value):
            raise serializers.ValidationError("Username must contain only letters.")
        return value

    def validate_email(self, value):
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w{2,4}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Enter a valid email address.")
        return value

    def validate_phone(self, value):
        phone_regex = r'^(010|011|012|015)\d{8}$'
        if not re.match(phone_regex, value):
            raise serializers.ValidationError("Phone number must start with 010, 011, 012, or 015 and be exactly 11 digits.")
        return value

    def validate_password(self, value):
        # Example strong password regex: Minimum 8 characters, at least 1 letter and 1 number and 1 special character
        password_regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(password_regex, value):
            raise serializers.ValidationError(
                "Password must be at least 8 characters long, include at least one letter, one number, and one special character."
            )
        validate_password(value)  # also apply Django's built-in password validators
        return value

    def validate(self, data):
        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return data

    def get(self, instance):
        return {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'phone': instance.phone,
            'role': instance.role,
            'status': instance.confirmed,
        }

    def create(self, validated_data):
        validated_data.pop('password2', None)  # remove password2 safely
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone', ''),
            role=validated_data.get('role', 'customer')
        )
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)

        password = validated_data.get('password')
        if not password:
            raise serializers.ValidationError("Password is required to update your profile data.")
        if not instance.check_password(password):
            raise serializers.ValidationError("Old password is incorrect.")
        
        password2 = validated_data.get('password2')
        if password2:
            self.validate_password(password2)
            instance.set_password(password2)
            print('Password updated')
        
        instance.save()
        return instance



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            "role": self.user.role,
        }
        return data