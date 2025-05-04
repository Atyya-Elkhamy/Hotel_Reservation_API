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
    def validate(self, data):
        username = data["username"]
        email = data["email"]
        password = data["password"]
        phone = data["phone"]
        if not re.fullmatch(r'[A-Za-z _]+', username):
            raise serializers.ValidationError({"username": "Only letters, spaces, and underscores are allowed."})
        data["username"] = re.sub(r'\s+', ' ', username).strip()
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            raise serializers.ValidationError({"email":"Invalid email format"})
        password_regex = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'
        if not re.match(password_regex, password):
            raise serializers.ValidationError({"password":"Password must be at least 8 characters long and include both letters and numbers"})
        phone_regex = r'^(010|012|015|011)\d{8}$'
        if not re.match(phone_regex, phone):
            raise serializers.ValidationError({"phone":"Phone number must be 11 digits and start with 010, 012, 015, or 011"})
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
        validated_data.pop('password2', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data['phone'],
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
    

class UserSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'role', 'password']
    def validate(self, data):
        username = data["username"]
        email = data["email"]
        password = data["password"]
        phone = data["phone"]
        if not re.fullmatch(r'[A-Za-z _]+', username):
            raise serializers.ValidationError({"username": "Only letters, spaces, and underscores are allowed."})
        data["username"] = re.sub(r'\s+', ' ', username).strip()
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            raise serializers.ValidationError({"email":"Invalid email format"})
        password_regex = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'
        if not re.match(password_regex, password):
            raise serializers.ValidationError({"password":"Password must be at least 8 characters long and include both letters and numbers"})
        phone_regex = r'^(010|012|015|011)\d{8}$'
        if not re.match(phone_regex, phone):
            raise serializers.ValidationError({"phone":"Phone number must be 11 digits and start with 010, 012, 015, or 011"})

        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data['phone'],
            role=validated_data.get('role', 'customer')
        )
        return user
