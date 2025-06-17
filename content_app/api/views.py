from ..models import Video
from rest_framework import viewsets
from .serializers import VideoSerializer
from rest_framework.permissions import AllowAny
from .permissions import IsAdminOrReadOnlyForAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

class VideoViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = VideoSerializer
    queryset = Video.objects.all()
    
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except:
            raise NotFound({'error':"video does not exist or is removed."})
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

        