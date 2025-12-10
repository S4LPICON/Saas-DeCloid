from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action

from django.db import transaction

import jwt
import redis
from jwt import InvalidTokenError
from datetime import datetime

from decloid.settings.base import SECRET_KEY
from applications.artifacts.models import Artifact
from .serializers import ArtifactSerializer, ArtifactBuildReportSerializer
from .artifact_repo_remover import delete_artifact_from_registry
from .redis_task_service import enqueue_build_task, r as redis_client
from .redis_task_service import BuildInProgressError



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
            print(
                f"Advertencia: El artifact {server_id_para_registry} se borró de la DB pero no del Registry."
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    # ------------------------
    #     BUILD ACTION FIX
    # ------------------------
    @action(detail=True, methods=['post'])
    def build(self, request, pk=None):
        artifact = self.get_object()

        # 1. Evitar builds simultáneos por DB
        existing = artifact.builds.filter(status__in=["pending", "running"]).exists()
        if existing:
            return Response(
                {"detail": "A build is already in progress"},
                status=400
            )

        # 🔥 CAMBIO DE ESTADO INMEDIATO
        artifact.status = "pending"
        artifact.save(update_fields=["status"])

        # 2. Crear el registro del build
        build_obj = artifact.builds.create(status="pending")

        # 3. Intentar mandar a Redis y adquirir el lock
        try:
            task_id, task_token = enqueue_build_task(
                artifact,
                build_id=str(build_obj.id)
            )
        except BuildInProgressError as e:
            # Si Redis dice que ya hay build, revertimos el build_obj
            build_obj.delete()
            artifact.status = "idle"
            artifact.save(update_fields=["status"])
            return Response({"detail": str(e)}, status=400)

        except redis.exceptions.ConnectionError:
            # Sin conexión a Redis → rollback
            build_obj.delete()
            artifact.status = "idle"
            artifact.save(update_fields=["status"])
            return Response(
                {"detail": "Could not connect to Redis server."},
                status=503
            )

        return Response(
            {
                "detail": "Build queued",
                "task_id": task_id,
                "build_id": str(build_obj.id)
            },
            status=202
        )

    # ------------------------
    #   BUILD REPORT (OK)
    # ------------------------
    @action(
        detail=True,
        methods=['post'],
        url_path="report",
        authentication_classes=[],
        permission_classes=[AllowAny]
    )
    def report_build(self, request, pk=None):
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

        if not artifact_uuid or not task_id:
            return Response({"error": "artifact_uuid or task_id missing in token"}, status=400)

        try:
            artifact = Artifact.objects.get(artifact_uuid=artifact_uuid)
        except Artifact.DoesNotExist:
            return Response({"error": "Artifact not found"}, status=404)

        serializer = ArtifactBuildReportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data

        # Transactional DB update
        try:
            with transaction.atomic():
                artifact.status = data["status"]
                
                artifact.size_in_mb = data.get("size_in_mb", artifact.size_in_mb)
                artifact.registry_path = data.get("registry_path", artifact.registry_path)
                artifact.logs = data.get("logs", artifact.logs)
                artifact.version = data.get("version") or artifact.version
                if data.get("updated_at"):
                    artifact.updated_at = data.get("updated_at")

                artifact.save()
        except Exception as e:
            return Response({"error": f"Database error: {str(e)}"}, status=500)

        # Update Redis & release lock
        try:
            redis_client.hset(
                f"build_status:{task_id}",
                mapping={
                    "status": data["status"],
                    "finished_at": datetime.utcnow().isoformat(),
                }
            )

            lock_key = f"artifact_lock:{artifact_uuid}"
            current = redis_client.get(lock_key)
            if current == task_id:
                redis_client.delete(lock_key)

            redis_client.delete(f"artifact_current_task:{artifact_uuid}")

        except Exception as e:
            print("Warning: Redis update failed:", e)
        
        try:
            build = artifact.builds.get(id=request.data["build_id"])
            build.status = data["status"]
            build.finished_at = datetime.utcnow()
            build.save()
        except:
            pass


        return Response({"ok": True}, status=200)
