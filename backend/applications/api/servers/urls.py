from django.urls import path
from .views import AvailableServerView
from rest_framework.routers import DefaultRouter
from .views import ServerViewSet

router = DefaultRouter()
router.register(r'', ServerViewSet, basename='server')

urlpatterns = [
    path('available/<uuid:artifact_uuid>/', AvailableServerView.as_view(), name='server-available'),
]

urlpatterns += router.urls
