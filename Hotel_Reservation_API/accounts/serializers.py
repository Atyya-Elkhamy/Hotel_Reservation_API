from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True, required=False, allow_blank=True)
    class Meta:
        model = User
        fields = ['id','username', 'email', 'phone', 'role','password', 'password2','confirmed']
        read_only_fields = ['id', 'confirmed']
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True}
        }

    def validate_password(self, value):
        validate_password(value)
        return value

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
        if validated_data['password'] != validated_data.get('password2'):
            raise serializers.ValidationError("Passwords do not match.")
        validate_password(validated_data['password'])
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
            raise serializers.ValidationError("password is required to update your profile data.")
        if not instance.check_password(password):
            raise serializers.ValidationError("Old password is incorrect.")
        password2 = validated_data.get('password2')
        if password and password2:
            if not instance.check_password(password):
                raise serializers.ValidationError("Old password is incorrect.")
            validate_password(password2)  # validate password strength
            instance.set_password(password2)
            print('password updated')
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