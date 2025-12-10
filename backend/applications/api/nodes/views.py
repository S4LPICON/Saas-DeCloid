import secrets
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Prefetch, ProtectedError

from applications.nodes.models import Node
from applications.servers.models import Server
from .serializers import NodeSerializer


class NodeViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Node.objects.all().prefetch_related(
        Prefetch('servers', queryset=Server.objects.all())
    )
    serializer_class = NodeSerializer

    # ----------------------
    # 🔥 FIX REAL AQUÍ
    # ----------------------
    def is_heartbeat(self, request):
        match = request.resolver_match
        if not match:
            return False
        return match.url_name == "node-heartbeat"

    def get_authenticators(self):
        if self.is_heartbeat(self.request):
            return []  # Sin JWT
        return super().get_authenticators()

    def get_permissions(self):
        if self.is_heartbeat(self.request):
            return [AllowAny()]
        return super().get_permissions()
    # ----------------------

    def get_queryset(self):
        if self.action == "heartbeat":
            return self.queryset  # sin filtro
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        key = secrets.token_hex(32)
        serializer.save(owner=self.request.user, key=   key)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {"detail": "No puedes eliminar este nodo porque tiene servidores asociados."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
    detail=True,
    methods=['post'],
    authentication_classes=[],
    permission_classes=[AllowAny],
    )
    def heartbeat(self, request, pk=None):
        node = self.get_object()
        node.is_online = True
        node.save(update_fields=["last_heartbeat", "is_online"])


        provided_key = request.headers.get("X-Node-Key")

        if not provided_key or provided_key != node.key:
            return Response(
                {"detail": "Invalid or missing node key"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Actualizar datos del nodo
        node.last_seen = timezone.now()
        node.status = Node.Status.ACTIVE

        node.docker_version = request.data.get("docker_version", node.docker_version)
        node.daemon_version = request.data.get("daemon_version", node.daemon_version)
        node.cpu_usage = request.data.get("cpu_usage", node.cpu_usage)
        node.memory_usage = request.data.get("memory_usage", node.memory_usage)
        node.storage_usage = request.data.get("storage_usage", node.storage_usage)

        node.save(update_fields=[
            'last_seen', 'status',
            'docker_version', 'daemon_version',
            'cpu_usage', 'memory_usage', 'storage_usage'
        ])

        return Response({"detail": "Heartbeat OK"}, status=200)
