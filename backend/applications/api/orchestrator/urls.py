from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServerOrchestratorViewSet
from django.urls import path
from applications.api.orchestrator.views import OrchestratorArtifactView

router = DefaultRouter()
# Ruta: /api/internal/register-server/
router.register(r'internal/register-server', ServerOrchestratorViewSet, basename='internal-server')

urlpatterns = [
    path('', include(router.urls)),
    path("orchestrator/artifacts/<uuid:artifact_id>/", OrchestratorArtifactView.as_view()),
]

# urls.py



