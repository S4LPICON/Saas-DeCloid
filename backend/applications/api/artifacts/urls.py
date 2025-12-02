# urls.py
from rest_framework.routers import DefaultRouter
from .views import ArtifactViewSet

router = DefaultRouter()
router.register(r'', ArtifactViewSet, basename='artifacts')

urlpatterns = router.urls
