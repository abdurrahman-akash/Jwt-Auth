from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .utils import send_verification_email
from django.utils.translation import gettext_lazy as _
from venv import logger


class BaseSerializer(serializers.ModelSerializer):
    """
    A base serializer for common functionality across all serializers.
    """
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'role', 'status', 'created_at', 'updated_at']    
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'password2', 'first_name', 'last_name', 'phone']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        user = CustomUser.objects.create(
            email = validated_data['email'],
            first_name = validated_data.get('first_name', ''),
            last_name = validated_data.get('last_name', ''),
            phone = validated_data.get('phone', ''),
        )
        user.set_password(validated_data['password'])
        try:
            send_verification_email(user)
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'role', 'status']
        read_only_fields = ['id', 'role', 'status', 'date_joined']
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['phone'] = user.phone
        token['role'] = user.role
        token['status'] = user.status
        return token

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, validators=[validate_password])
    token = serializers.CharField(required=True)
