from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CheckUserSerializer, LogInSerializer, RegisterSerializer, ActivateUserSerializer
from django.contrib.auth import login
from rest_framework.authtoken.models import Token


class CheckUserExistsView(GenericAPIView):
    serializer_class = CheckUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = CheckUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(False, status=status.HTTP_200_OK)
        return Response(True, status=status.HTTP_200_OK)


class LogInView(GenericAPIView):
    # authentication_classes = []
    # permission_classes = [AllowAny]
    serializer_class = LogInSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            data = {"token": token.key, "email": user.email}
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        data={}
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data={
                'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email,
            }
            return Response(data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors ,status=status.HTTP_400_BAD_REQUEST)
    
    
class ActivateUserView(GenericAPIView):
    serializer_class = ActivateUserSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Account erfolgreich aktiviert.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)