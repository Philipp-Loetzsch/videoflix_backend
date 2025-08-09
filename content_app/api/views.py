from ..models import Video
from rest_framework import viewsets
from .serializers import VideoSerializer
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
import os
from django.views import View
from django.http import FileResponse, Http404, HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from .mixins import CORSMixin
from user_app.authentication import CookieJWTAuthentication


class VideoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Video model CRUD operations.
    Uses cookie-based JWT authentication.
    """
    authentication_classes = [CookieJWTAuthentication]
    serializer_class = VideoSerializer
    queryset = Video.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single video instance.
        
        Args:
            request: The HTTP request
            *args, **kwargs: Additional arguments
            
        Returns:
            Response: The serialized video data with HTTPS URLs
            
        Raises:
            NotFound: If the video doesn't exist or has been removed
        """
        try:
            instance = self.get_object()
        except:
            raise NotFound({"error": "video does not exist or is removed."})
        serializer = self.get_serializer(instance)
        data = serializer.data

        if hasattr(instance, 'file') and hasattr(instance.file, 'url'):
         data['file'] = request.build_absolute_uri(instance.file.url).replace("http://", "https://")

        return Response(data)


class HLSSegmentView(CORSMixin, APIView):
    """
    View for serving HLS video segments with CORS support.
    Uses cookie-based JWT authentication.
    """
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, movie_id, resolution, segment):
        """
        Get a specific HLS video segment.
        
        Args:
            request: The HTTP request
            movie_id: ID of the video
            resolution: Video resolution (e.g., '720p')
            segment: The segment filename
            
        Returns:
            FileResponse: The video segment file with appropriate CORS headers
            
        Raises:
            Http404: If video or segment is not found
        """
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
    """
    View for serving HLS playlists with CORS support.
    Uses cookie-based JWT authentication.
    """

    authentication_classes = [CookieJWTAuthentication]
    
    def get(self, request, movie_id, resolution):
        """
        Get the HLS playlist for a specific video and resolution.
        
        Args:
            request: The HTTP request
            movie_id: ID of the video
            resolution: Video resolution (e.g., '720p')
            
        Returns:
            FileResponse: The M3U8 playlist file with appropriate CORS headers
            
        Raises:
            Http404: If video or playlist is not found
        """
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
            content = content.replace(
                'videos/',
                'https://v-backend.webdevelopment-loetzsch.de/media/videos/'
            )
            content = content.replace(
                'http://v-backend.webdevelopment-loetzsch.de',
                'https://v-backend.webdevelopment-loetzsch.de'
            )
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
