from rest_framework import routers
from .views import VideoViewSet, HLSSegmentView,HLSPlaylistView
from django.urls import path

app_name = 'content_app'

router = routers.SimpleRouter()
router.register(r'video', VideoViewSet)

urlpatterns = router.urls + [
     path('video/<int:movie_id>/<str:resolution>/index.m3u8/', HLSPlaylistView.as_view(), name='video-playlist'),
     path('video/<int:movie_id>/<str:resolution>/<str:segment>/', HLSSegmentView.as_view(), name='video-segment'),
]

