from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action

from decloid.settings.base import SECRET_KEY

from .artifact_repo_remover import delete_artifact_from_registry
from applications.artifacts.models import Artifact
from .serializers import ArtifactSerializer
from rest_framework.permissions import AllowAny
from .redis_task_service import enqueue_build_task
import jwt
from jwt import InvalidTokenError
from datetime import datetime, timedelta
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from applications.artifacts.models import Artifact
from .serializers import ArtifactBuildReportSerializer
from .redis_task_service import enqueue_build_task
import redis

# Conexión global a Redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)


class ArtifactViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Artifact.objects.all()
    serializer_class = ArtifactSerializer
    
    def get_queryset(self):
        return Artifact.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        server_id_para_registry = str(instance.artifact_uuid)

        self.perform_destroy(instance)
        
        success = delete_artifact_from_registry(server_id_para_registry)
        if not success:
            print(f"Advertencia: El artifact {server_id_para_registry} se borró de la DB pero no del Registry.")

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def build(self, request, pk=None):
        artifact = self.get_object()

        try:
            task_id = enqueue_build_task(artifact)
        except ConnectionError:
            return Response(
                {"detail": "Could not connect to Redis server."},
                status=503
            )

        return Response(
            {"detail": "Build started", "task_id": task_id},
            status=202
        )
    
    @action(
        detail=True,
        methods=['post'],
        url_path="report",
        authentication_classes=[],
        permission_classes=[AllowAny]
    )
    def report_build(self, request, pk=None):
        """
        Endpoint usado por los workers para reportar resultados de builds.
        Usa JWT para autenticar y asegura que no se rompa la base de datos.
        """
        # 1️⃣ Validar token JWT
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return Response({"error": "Missing token"}, status=401)

        token = auth.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except InvalidTokenError:
            return Response({"error": "Invalid or expired token"}, status=403)

        task_id = payload.get("task_id")
        artifact_uuid = payload.get("artifact_uuid")

        if not artifact_uuid:
            return Response({"error": "artifact_uuid missing in token"}, status=400)

        # 2️⃣ Obtener artifact
        try:
            artifact = Artifact.objects.get(artifact_uuid=artifact_uuid)
        except Artifact.DoesNotExist:
            return Response({"error": "Artifact not found"}, status=404)

        # 3️⃣ Validar payload del build
        serializer = ArtifactBuildReportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data

        # 4️⃣ Validación adicional: version requerida si build fue exitoso
        if data["status"] == "success" and not data.get("version"):
            return Response({"error": "version is required for successful builds"}, status=400)

        # 5️⃣ Actualizar artifact de forma segura
        artifact.status = data["status"]
        artifact.size_in_mb = data.get("size_in_mb", artifact.size_in_mb)
        artifact.registry_path = data.get("registry_path", artifact.registry_path)
        artifact.logs = data.get("logs", artifact.logs)
        artifact.version = data.get("version") or artifact.version
        artifact.updated_at = data.get("update_date", artifact.update_date)

        try:
            artifact.save()
        except Exception as e:
            # Captura errores de DB (por ejemplo NOT NULL)
            return Response({"error": f"Database error: {str(e)}"}, status=500)

        return Response({"ok": True}, status=200)