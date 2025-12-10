import secrets
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_ipv46_address
from django.utils import timezone

from applications.artifacts.models import Artifact
from applications.nodes.models import Node

class Server(models.Model):
    
    """
    Representa un servidor de Minecraft desplegado en un Node específico.
    
    Cada servidor está asociado a un Artifact (imagen Docker) que define su 
    configuración y versión de juego. Contiene información sobre recursos 
    asignados, estado operativo, ubicación en la red (IP/puerto), métricas 
    de uso (jugadores en línea) y datos de gestión del contenedor Docker.

    Relaciones clave:
    - owner: Usuario que posee el servidor.
    - node: Nodo físico/virtual donde corre el servidor.
    - artifact: Imagen que define el servidor (mods, plugins, versión de Minecraft).
    """
    
    class Status(models.TextChoices):
        PROVISIONING = "provisioning", "Provisioning"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        MAINTENANCE = "maintenance", "Maintenance"

    server_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="servers")
    name = models.CharField(max_length=100)

    node = models.ForeignKey(Node, on_delete=models.PROTECT, related_name="servers")
    artifact = models.ForeignKey(Artifact, on_delete=models.CASCADE, related_name="servers")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROVISIONING)
    ip_address = models.CharField(max_length=45, validators=[validate_ipv46_address])
    port = models.PositiveIntegerField()
    
    tps = models.FloatField(default=0)

    players_online = models.PositiveIntegerField(default=0)
    max_players = models.PositiveIntegerField(default=20)

    cpu_allocated = models.PositiveIntegerField(editable=False)
    memory_allocated = models.PositiveIntegerField(editable=False)

    last_seen = models.DateTimeField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    uptime = models.BigIntegerField(default=0)
    
    key = models.CharField(max_length=128, default=secrets.token_hex(32))
    last_heartbeat = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=False)

    temp_logs_path = models.CharField(max_length=255, blank=True, null=True)
    docker_container_id = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        ordering = ['-create_date']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['status']),
            models.Index(fields=['node']),
        ]

    def __str__(self):
        return f"{self.name} ({self.status})"

    def save(self, *args, **kwargs):
        if self.artifact:
            self.cpu_allocated = self.artifact.cpu_cores
            self.memory_allocated = self.artifact.memory_in_mb
        super().save(*args, **kwargs)

    @property
    def uptime_seconds(self):
        if self.last_seen:
            return int((timezone.now() - self.last_seen).total_seconds())
        return self.uptime
