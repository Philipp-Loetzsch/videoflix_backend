from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CheckUserSerializer, RegisterSerializer, ActivateUserSerializer, CustomTokenObtainPairSerializer
from django.contrib.auth import login
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

class CheckUserExistsView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CheckUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = CheckUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(False, status=status.HTTP_200_OK)
        return Response(True, status=status.HTTP_200_OK)

class RegisterView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        data={}
        if serializer.is_valid():
            saved_account = serializer.save()
            # token, created = Token.objects.get_or_create(user=saved_account)
            data={
                # 'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email,
            }
            return Response(data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors ,status=status.HTTP_400_BAD_REQUEST)
    
    
class ActivateUserView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ActivateUserSerializer
    
    def post(self, request):
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Account erfolgreich aktiviert.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST),
    
class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        
        refresh = serializer.validated_data["refresh"]
        access = serializer.validated_data["access"]
        response = Response({"message":"Login successful"})
        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        return response
    
class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        
        if refresh_token is None:
            return Response(
                {"details": "Refresh token not found!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer = self.get_serializer(data={"refresh":refresh_token})
        
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
            samesite="Lax"
        )
        
        return response