from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

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

        user = authenticate(username=user_obj.username, password=password)

        if user is None:
            raise serializers.ValidationError({'detail': 'Invalid credentials'})
      
        if not user.is_active:
            raise serializers.ValidationError({'detail': 'User account is disabled.'})

        data['user'] = user 
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

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_active = False
        user.save()
        return user
