from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.core.signing import TimestampSigner
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()
signer = TimestampSigner()

class CheckUserSerializer(serializers.Serializer):
    """Check user existence by email."""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Validate email existence."""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

class RegisterSerializer(serializers.Serializer):
    """Handle new user registration."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)
    repeated_password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        """Check if email is not already registered."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User does already exist.")
        return value

    def validate(self, data):
        """Validate that passwords match."""
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError("Passwords don't match.")
        return data

    def create(self, validated_data):
        """Create and save new inactive user."""
        email = validated_data["email"]
        password = validated_data["password"]
        username = email.split("@")[0]

        user = User(username=username, email=email, is_active=False)
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
        token = self.validated_data["token"]
        user = User.objects.get(auth_token__key=token)
        user.is_active = True
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Token serializer using email for authentication."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        """Remove username field."""
        super().__init__(*args, **kwargs)

        if "username" in self.fields:
            self.fields.pop("username")

    def validate(self, attrs):
        """Validate email and password."""
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid credentials"})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "User is disabled"})

        user = authenticate(username=user.username, password=password)
        if user is None:
            raise serializers.ValidationError({"detail": "Invalid credentials"})

        return super().validate({"username": user.username, "password": password})

class ForgotPasswordSerializer(serializers.Serializer):
    """Handle forgot password requests."""
    email = serializers.EmailField()
     
    def validate_email(self, value):
        """Check if email exists."""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is not registered")
        return value

class ChangePasswordSerializer(serializers.Serializer):
    """Handle password change requests."""
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    repeated_new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        """Validate password change request and token."""
        if data["new_password"] != data["repeated_new_password"]:
            raise serializers.ValidationError("Passwords don't match.")

        try:
            uid = urlsafe_base64_decode(data["uidb64"]).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError({"detail": "Invalid user ID."})

        if not default_token_generator.check_token(user, data["token"]):
            raise serializers.ValidationError({"detail": "Invalid or expired token."})

        data["user"] = user
        return data
