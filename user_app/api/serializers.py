from django.contrib.auth import authenticate
# from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CheckUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

class LogInSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
             raise serializers.ValidationError("Email and password are required.", code='authorization')

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': 'user does not exist'})

        if not check_password(password, user_obj.password):
            raise serializers.ValidationError({"detail": "Invalid credentials."})
        
        if not user_obj.is_active :
             raise serializers.ValidationError({'detail': 'User is disabled'})
      
        data['user'] = user_obj 
        return data
    
class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)
    repeated_password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User does already exist.")
        return value

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwords don't match.")
        return data

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        username = email.split('@')[0]

        user = User(
            username=username,
            email=email,
            is_active = False
        )
        user.set_password(password)
        user.save()
        return user
    
class ActivateUserSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            user = User.objects.get(auth_token__key=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Ungültiger Token.")
        if user.is_active:
            raise serializers.ValidationError("Benutzer ist bereits aktiviert.")
        return value

    def save(self):
        token = self.validated_data['token']
        user = User.objects.get(auth_token__key=token)
        user.is_active = True
        user.save()
        return user
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if "username"in self.fields:
            self.fields.pop("username")
    
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': 'user does not exist'})

        if not check_password(password, user.password):
            raise serializers.ValidationError({"detail": "Invalid credentials."})
        
        if not user.is_active :
             raise serializers.ValidationError({'detail': 'User is disabled'})
        
        data = super().validate({"username":user.username, "password": password})
        return data