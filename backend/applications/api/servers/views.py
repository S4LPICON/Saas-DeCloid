from django.utils import timezone
from rest_framework import viewsets
from applications.servers.models import Server
from .serializers import ServerSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.authentication import JWTAuthentication

class ServerViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    
    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(owner=user)
    
    def perform_create(self, serializer):
        # asigna automáticamente el owner
        serializer.save(owner=self.request.user)


    @action(detail=True, methods=['post'])
    def heartbeat(self, request, pk=None):
        server = self.get_object()

        # actualizar valores enviados por el nodo
        server.last_seen = timezone.now()
        server.status = Server.Status.ACTIVE

        # campos que manda el nodo
        server.docker_version = request.data.get("docker_version", server.docker_version)
        server.daemon_version = request.data.get("daemon_version", server.daemon_version)
        server.cpu_usage = request.data.get("cpu_usage", server.cpu_usage)
        server.memory_usage = request.data.get("memory_usage", server.memory_usage)
        server.storage_usage = request.data.get("storage_usage", server.storage_usage)

        server.save(update_fields=[
            'last_seen', 'status', 'docker_version', 'daemon_version',
            'cpu_usage', 'memory_usage', 'storage_usage'
        ])

        return Response({"detail": "Heartbeat received"}, status=status.HTTP_200_OK)
