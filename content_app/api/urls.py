from rest_framework import routers
from .views import VideoViewSet
from django.urls import path

app_name = 'content_app'

router = routers.SimpleRouter()
router.register(r'video', VideoViewSet)

urlpatterns = router.urls 

