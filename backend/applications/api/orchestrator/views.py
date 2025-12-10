from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from .serializers import ServerOrchestratorSerializer
from applications.servers.models import Server
    #----------------------
    # applications/api/orchestrator/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from applications.artifacts.models import Artifact
from applications.api.auth.orchestrator_auth import OrchestratorAuthentication
from applications.api.artifacts.serializers import ArtifactSerializer

# --- Permiso Personalizado ---
class IsOrchestratorUser(permissions.BasePermission):
    """
    Solo permite acceso si el usuario se llama 'orchestrator_bot' 
    (o es superusuario). NADIE LO ESTA USANDO.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.username == 'orchestrator_bot' or request.user.is_superuser)
        )

# --- La Vista Blindada ---
class ServerOrchestratorViewSet(viewsets.ModelViewSet):
    authentication_classes = [OrchestratorAuthentication]
    # Ahora exigimos que esté autenticado Y que sea el bot
    permission_classes = [AllowAny]
    
    queryset = Server.objects.all()
    serializer_class = ServerOrchestratorSerializer

    def create(self, request, *args, **kwargs):
        # El serializer espera 'owner', 'node', 'artifact' en el JSON.
        # Como es el orquestador, confiamos en los datos que envía.
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


class OrchestratorArtifactView(APIView):
    authentication_classes = [OrchestratorAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, artifact_id):
        try:
            artifact = Artifact.objects.get(artifact_uuid=artifact_id)
        except Artifact.DoesNotExist:
            return Response({"detail": "Artifact not found"}, status=404)

        return Response(ArtifactSerializer(artifact).data)
