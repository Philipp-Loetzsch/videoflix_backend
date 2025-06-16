from rest_framework import routers
from .views import VideoViewSet

router = routers.SimpleRouter()
router.register(r'content', VideoViewSet)
urlpatterns = router.urls

