from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CheckUserSerializer, LogInSerializer, RegisterSerializer
from django.contrib.auth import login
from rest_framework.authtoken.models import Token


class CheckUserExistsView(GenericAPIView):
    serializer_class = CheckUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(False)
        return Response(True, status=status.HTTP_200_OK)


class LogInView(GenericAPIView):
    # authentication_classes = []
    # permission_classes = [AllowAny]
    serializer_class = LogInSerializer

    def post(self, request):
        serializer = LogInSerializer(data=request.data)
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
        serializer = RegisterSerializer(data=request.data)
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
        
        return Response(serializer.error_messages ,status=status.HTTP_400_BAD_REQUEST)