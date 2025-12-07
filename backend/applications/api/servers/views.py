from django.utils import timezone
from rest_framework import viewsets
from applications.api.auth.orchestrator_auth import OrchestratorAuthentication
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


#--------------
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from applications.servers.models import Server
from applications.artifacts.models import Artifact
from applications.nodes.models import Node
from applications.api.servers.serializers import ServerMinimalSerializer


class AvailableServerView(APIView):
    """
    Retorna la primera instancia del artifact que:
    - esté activa
    - no esté llena
    """
    authentication_classes = [OrchestratorAuthentication]

    def get(self, request, artifact_uuid):
        try:
            artifact = Artifact.objects.get(artifact_uuid=artifact_uuid)
        except Artifact.DoesNotExist:
            return Response(
                {"error": "Artifact not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # filtrar servers activos de este artifact
        instances = Server.objects.filter(
            artifact=artifact,
            status="provisioning"               # o el status que uses
        )

        # buscar el primero NO lleno
        for inst in instances:
            if inst.players_online < inst.max_players:
                data = {
                    "name": inst.name,
                    "ip_address": inst.node.ip_address,
                    "port": inst.port,
                    "players_online": inst.players_online,
                    "max_players": inst.max_players,
                }
                return Response(data, status=status.HTTP_200_OK)

        return Response({"available": False}, status=status.HTTP_200_OK)
