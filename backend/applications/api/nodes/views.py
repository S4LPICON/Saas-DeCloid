from django.utils import timezone
from rest_framework import viewsets
from applications.nodes.models import Node
from .serializers import NodeSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.db.models import Prefetch
from rest_framework import viewsets
from applications.nodes.models import Node
from applications.servers.models import Server
from .serializers import NodeSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import ProtectedError


from rest_framework_simplejwt.authentication import JWTAuthentication

class NodeViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Node.objects.all().prefetch_related(
        Prefetch('servers', queryset=Server.objects.all())
    )
    serializer_class = NodeSerializer
    
    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(owner=user)
    
    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user,
            subscription=getattr(self.request.user, 'subscription', None)
        )

        
        
    def destroy(self, request, *args, **kwargs):
            instance = self.get_object()
            try:
                self.perform_destroy(instance)
            except ProtectedError:
                return Response(
                    {
                        "detail": "No puedes eliminar este nodo porque tiene servidores asociados. "
                                "Elimina primero los servidores."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def heartbeat(self, request, pk=None):
        node = self.get_object()

        # actualizar valores enviados por el nodo
        node.last_seen = timezone.now()
        node.status = Node.Status.ACTIVE

        # campos que manda el nodo
        node.docker_version = request.data.get("docker_version", node.docker_version)
        node.daemon_version = request.data.get("daemon_version", node.daemon_version)
        node.cpu_usage = request.data.get("cpu_usage", node.cpu_usage)
        node.memory_usage = request.data.get("memory_usage", node.memory_usage)
        node.storage_usage = request.data.get("storage_usage", node.storage_usage)

        node.save(update_fields=[
            'last_seen', 'status', 'docker_version', 'daemon_version',
            'cpu_usage', 'memory_usage', 'storage_usage'
        ])

        return Response({"detail": "Heartbeat received"}, status=status.HTTP_200_OK)
