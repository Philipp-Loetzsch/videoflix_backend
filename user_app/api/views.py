from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CheckUserSerializer

class CheckUserExistsView(GenericAPIView):
    serializer_class = CheckUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(False)

        return Response(True, status=status.HTTP_200_OK)
