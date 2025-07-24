from rest_framework import serializers
from ..models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [
            'id',
            'uuid',
            'title',
            'description',
            'file',
            'preview',
            'thumbnail',
            'preview_title',
            'duration',
            'category',
            'created_at',
            'hls_playlist',
        ]
        read_only_fields = ['id', 'created_at', 'duration', 'hls_playlist']
