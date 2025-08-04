from ..models import Video
from rest_framework import viewsets
from .serializers import VideoSerializer
from .permissions import IsAdminOrReadOnlyForAuthenticated
from rest_framework.exceptions import NotFound, AuthenticationFailed
from rest_framework.response import Response
import os
from django.views import View
from django.http import FileResponse, Http404, HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from .mixins import CORSMixin
from user_app.authentication import CookieJWTAuthentication


class VideoViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAdminOrReadOnlyForAuthenticated]
    authentication_classes = [CookieJWTAuthentication]
    serializer_class = VideoSerializer
    queryset = Video.objects.all()

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except:
            raise NotFound({"error": "video does not exist or is removed."})
        serializer = self.get_serializer(instance)
        data = serializer.data

        # HTTPS-URL erzwingen, falls .file vorhanden
        if hasattr(instance, 'file') and hasattr(instance.file, 'url'):
         data['file'] = request.build_absolute_uri(instance.file.url).replace("http://", "https://")

        return Response(data)


class HLSSegmentView(CORSMixin, APIView):
    # permission_classes = [IsAdminOrReadOnlyForAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, movie_id, resolution, segment):
        try:
            video = Video.objects.get(pk=movie_id)
        except Video.DoesNotExist:
            raise Http404("Video nicht gefunden")
        
        video_folder = f"{video.title}_{video.uuid}"
        filename = f"{resolution}_{segment}"
        segment_path = os.path.join(
            settings.MEDIA_ROOT, "videos", video_folder, "hls", filename
        )
        
        if not os.path.exists(segment_path):
            raise Http404("Segment nicht gefunden")

        response = FileResponse(open(segment_path, "rb"), content_type="video/MP2T")
        response["Access-Control-Allow-Origin"] = "https://videoflix.webdevelopment-loetzsch.de"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "*"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    def options(self, request, *args, **kwargs):
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "https://videoflix.webdevelopment-loetzsch.de"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "*"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

class HLSPlaylistView(CORSMixin, APIView):
    # permission_classes = [IsAdminOrReadOnlyForAuthenticated]
    authentication_classes = [CookieJWTAuthentication]
    
    def get(self, request, movie_id, resolution):
        try:
            video = Video.objects.get(pk=movie_id)
        except Video.DoesNotExist:
            raise Http404("Video nicht gefunden")

        video_folder = f"{video.title}_{video.uuid}"
        filename = f"{resolution}.m3u8"

        playlist_path = os.path.join(
            settings.MEDIA_ROOT,
            "videos",
            video_folder,
            "hls",
            filename
        )

        if not os.path.exists(playlist_path):
            raise Http404("Playlist nicht gefunden")

        with open(playlist_path, 'r') as f:
            content = f.read()
            # First ensure all relative paths are converted to absolute HTTPS URLs
            content = content.replace(
                'videos/',
                'https://v-backend.webdevelopment-loetzsch.de/media/videos/'
            )
            # Replace any remaining HTTP URLs with HTTPS
            content = content.replace(
                'http://v-backend.webdevelopment-loetzsch.de',
                'https://v-backend.webdevelopment-loetzsch.de'
            )
            # Handle any absolute paths that might not have the domain
            content = content.replace(
                '/media/videos/',
                'https://v-backend.webdevelopment-loetzsch.de/media/videos/'
            )

        response = FileResponse(
            content.encode(), 
            content_type="application/vnd.apple.mpegurl"
        )
        response["Access-Control-Allow-Origin"] = "https://videoflix.webdevelopment-loetzsch.de"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "*"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    def options(self, request, *args, **kwargs):
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "https://videoflix.webdevelopment-loetzsch.de"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "*"
        response["Access-Control-Allow-Credentials"] = "true"
        return response
