from ..models import Video
from rest_framework import viewsets
from .serializers import VideoSerializer
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from user_app.authentication import CookieJWTAuthentication


class VideoViewSet(viewsets.ReadOnlyModelViewSet):
    """ReadOnly ViewSet for Video model, admin changes via admin panel."""
    authentication_classes = [CookieJWTAuthentication]
    serializer_class = VideoSerializer
    queryset = Video.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """Retrieve single video instance with HTTPS URLs."""
        try:
            instance = self.get_object()
        except:
            raise NotFound({"error": "video does not exist or is removed."})
        serializer = self.get_serializer(instance)
        data = serializer.data

        if hasattr(instance, 'file') and hasattr(instance.file, 'url'):
         data['file'] = request.build_absolute_uri(instance.file.url).replace("http://", "https://")

        return Response(data)