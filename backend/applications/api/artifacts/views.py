# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action

from applications.artifacts.models import Artifact
from .serializers import ArtifactSerializer
from .redis_task_service import enqueue_build_task

class ArtifactViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Artifact.objects.all()
    serializer_class = ArtifactSerializer
    
    def get_queryset(self):
        return Artifact.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def build(self, request, pk=None):
        artifact = self.get_object()

        # crear tarea
        task_id = enqueue_build_task(artifact)

        return Response(
            {"detail": "Build started", "task_id": task_id},
            status=202
        )