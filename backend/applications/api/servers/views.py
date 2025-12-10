from django.utils import timezone
from rest_framework import viewsets
from applications.api.auth.orchestrator_auth import OrchestratorAuthentication
from applications.servers.models import Server
from .serializers import ServerSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

class ServerViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    
    def get_object(self):
        # si estás en la acción heartbeat -> ignora owner=request.user
        if self.action == "heartbeat":
            return Server.objects.get(pk=self.kwargs["pk"])
        return super().get_object()

    
    def perform_create(self, serializer):
        # asigna automáticamente el owner
        serializer.save(owner=self.request.user)


    @action(
        detail=True,
        methods=['post'],
        authentication_classes=[],
        permission_classes=[AllowAny],
    )
    def heartbeat(self, request, pk=None):
        server = self.get_object()
        server.is_online = True
        server.save(update_fields=["last_heartbeat", "is_online"])
        
        provided_key = request.headers.get("X-Server-Key")
        if not provided_key or provided_key != server.key:
            return Response(
                {"detail": "Invalid or missing server key"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        server.last_seen = timezone.now()
        server.status = Server.Status.ACTIVE

        server.players_online = request.data.get("players", server.players_online)
        server.tps = request.data.get("tps", server.tps)

        server.save(update_fields=['last_seen', 'status', 'players_online', 'tps'])

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
