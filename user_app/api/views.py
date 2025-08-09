from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import (
    CheckUserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    ForgotPasswordSerializer,
    ChangePasswordSerializer
)
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.core.signing import TimestampSigner
from django.contrib.auth import get_user_model
from django.dispatch import Signal
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

signer = TimestampSigner()
User = get_user_model()
send_reset_email_signal = Signal()

class CheckUserExistsView(GenericAPIView):
    """
    API view to check if a user exists based on provided data.
    """
    permission_classes = [AllowAny]
    serializer_class = CheckUserSerializer

    def post(self, request, *args, **kwargs):
        """
        Check if the user exists with the given data.
        Returns True if valid, otherwise False.
        """
        serializer = CheckUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(False, status=status.HTTP_200_OK)
        return Response(True, status=status.HTTP_200_OK)


class RegisterView(GenericAPIView):
    """
    API view to register a new user account.
    """
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        """
        Register a new user with the provided data.
        Returns the username and email if successful, otherwise errors.
        """
        serializer = self.get_serializer(data=request.data)
        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            data = {
                "username": saved_account.username,
                "email": saved_account.email,
            }
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActivateUserView(GenericAPIView):
    """
    API view to activate a user account via email link.
    """
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        """
        Activate the user account if the token is valid.
        Returns a message indicating the result.
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"message": "Ungültiger Link"}, status=400)

        if user.is_active:
            return Response({"message": "Benutzer ist bereits aktiviert."}, status=400)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Account successfully activated."}, status=200)

        return Response({"message": "Aktivierung fehlgeschlagen."}, status=400)

class CookieTokenObtainPairView(TokenObtainPairView):
    """
    API view to obtain JWT tokens and set them as cookies.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """
        Obtain JWT access and refresh tokens and set them as cookies.
        Returns a message on successful login.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh = serializer.validated_data["refresh"]
        access = serializer.validated_data["access"]
        response = Response({"message": "Login successful"})
        response.set_cookie(
            key="access_token", value=access, httponly=True, secure=True, samesite="Lax"
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=True,
            samesite="None",
        )
        return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    API view to refresh JWT access token using the refresh token from cookies.
    """
    def post(self, request, *args, **kwargs):
        """
        Refresh the JWT access token using the refresh token from cookies.
        Returns a message on success or error details.
        """
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"details": "Refresh token not found!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response(
                {"details": "Refresh token invalid!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = serializer.validated_data.get("access")

        response = Response({"message": "access Token refreshed"})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="None",
        )
        return response

class CookieTokenRemoveView(APIView):
    """
    API view to remove JWT tokens from cookies and blacklist the refresh token.
    """
    def post(self, request, *args, **kwargs):
        """
        Blacklist the refresh token and remove it from cookies to log out the user.
        Returns a logout confirmation message.
        """
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass

        response = Response({"detail": "Logout erfolgreich"})
        response.delete_cookie("refresh_token")
        return response

class ForgotPasswordView(GenericAPIView):
    """
    API view to handle forgot password requests and send reset emails.
    """
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]
    def post(self, request):
        """
        Send a password reset email if the user with the given email exists.
        Always returns 200 status for security reasons.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
            send_reset_email_signal.send(sender=self.__class__, user=user)
        except User.DoesNotExist:
            pass

        return Response(status=200)

class ChangePasswordView(GenericAPIView):
    """
    API view to change/reset the user's password using a token.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """
        Change the user's password if the token is valid.
        Returns a confirmation message on success.
        """
        data = {
            "uidb64": uidb64,
            "token": token,
            "new_password": request.data.get("new_password"),
            "repeated_new_password": request.data.get("repeated_new_password"),
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"detail": "Your Password has been successfully reset."}, status=200)
