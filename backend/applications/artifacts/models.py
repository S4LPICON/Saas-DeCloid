import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings
import os
import uuid
import shutil
from django.core.files.storage import FileSystemStorage

from applications.artifacts.DEFAULT_DOCKER_FILES import DEFAULT_DOCKERFILES

def artifact_upload_path(instance, filename):
    user_id = str(instance.owner.id)
    artifact_uuid = str(instance.artifact_uuid)

    return os.path.join(
        "users_data",
        user_id,
        artifact_uuid,
        filename
    )


class Artifact(models.Model):
    
    """
    Representa una imagen Docker de un servidor Minecraft.
    Incluye información sobre su origen, recursos requeridos y estado.
    """
    
    
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        MAINTENANCE = "maintenance", "Maintenance",
        NOT_BUILDED  = "not_builded", "Not Builded",
        READY = "ready", "Ready",
        ERROR = "error", "Error"

    class Type(models.TextChoices):
        PAPER = "paper", "PaperMC"
        SPIGOT= "spigot", "SpigotMC"
        FABRIC = "fabric", "Fabric"
        FORGE = "forge", "Forge"

    artifact_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="artifacts")
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=50, default="not builded")
    description = models.TextField(max_length=128)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.PAPER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_BUILDED)

    java_version = models.CharField(max_length=20)
    mc_version = models.CharField(max_length=20)
    size_in_mb = models.PositiveIntegerField(validators=[MinValueValidator(1)], null=True)
    
    cpu_cores = models.PositiveIntegerField(default=1)
    memory_in_mb = models.PositiveIntegerField(default=512)

    #root_path = models.FileField(upload_to='artifacts/source_files/')
    zip_file = models.FileField(upload_to=artifact_upload_path, blank=True, null=True)
    registry_path = models.CharField(max_length=255, blank=True, null=True)
    
    dockerfile_name = models.CharField(max_length=50, choices=[(k, k) for k in DEFAULT_DOCKERFILES.keys()], default="paper")
    dockerfile_custom = models.TextField(blank=True, null=True)

    logs = models.TextField(blank=True, null=True)
    
    #flags = models.JSONField(blank=True, null=True)
    active_instances = models.PositiveIntegerField(default=0)

    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creation_date']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['type', 'status']),
        ]

    def delete(self, *args, **kwargs):
        # Ruta del archivo
        file_path = self.zip_file.path
        
        # Carpeta contenedora (/users_data/<id>/<artifact_uuid>/)
        folder = os.path.dirname(file_path)

        # Primero borra el archivo y el registro
        super().delete(*args, **kwargs)

        # Luego borra la carpeta completa
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    def __str__(self):
        return f"{self.name} v{self.version} ({self.type})"


class ArtifactBuild(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        RUNNING = "running"
        SUCCESS = "success"
        FAILED = "failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artifact = models.ForeignKey(Artifact, on_delete=models.CASCADE, related_name="builds")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    logs = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
