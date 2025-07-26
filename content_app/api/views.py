from ..models import Video
from rest_framework import viewsets
from .serializers import VideoSerializer
from .permissions import IsAdminOrReadOnlyForAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
import os
from django.views import View
from django.http import FileResponse, Http404
from django.conf import settings


class VideoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnlyForAuthenticated]
    serializer_class = VideoSerializer
    queryset = Video.objects.all()

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except:
            raise NotFound({"error": "video does not exist or is removed."})
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class HLSSegmentView(View):
    permisson_classes = [IsAdminOrReadOnlyForAuthenticated]

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
        print(f"Suche Segment unter: {segment_path}")
        if not os.path.exists(segment_path):
            raise Http404("Segment nicht gefunden")

        return FileResponse(open(segment_path, "rb"), content_type="video/MP2T")

class HLSPlaylistView(View):
    permisson_classes = [IsAdminOrReadOnlyForAuthenticated]
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

        print(f"Pfad zur Playlist: {playlist_path}")

        if not os.path.exists(playlist_path):
            raise Http404("Playlist nicht gefunden")

        return FileResponse(open(playlist_path, "rb"), content_type="application/vnd.apple.mpegurl")
