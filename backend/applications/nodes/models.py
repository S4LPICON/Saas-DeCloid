import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_ipv46_address
from applications.billing.models import UserSubscription

class Node(models.Model):
    
    """
    Representa un nodo físico o virtual donde se ejecutan servidores de Minecraft.
    Incluye información de recursos, estado, propietario y suscripción.
    """
    
    class Status(models.TextChoices):
        PROVISIONING = "provisioning", "Provisioning"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        MAINTENANCE = "maintenance", "Maintenance"
        UNHEALTHY = "unhealthy", "Unhealthy"
        DECOMMISSIONED = "decommissioned", "Decommissioned"

    node_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="nodes")
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name="nodes")
    name = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=45, validators=[validate_ipv46_address])
    location = models.CharField(max_length=32)

    api_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROVISIONING)

    cpu_cores = models.PositiveIntegerField()
    cpu_usage = models.FloatField(default=0.0)
    cpu_over_allocation = models.FloatField(default=1.0)

    memory = models.PositiveIntegerField(help_text="Memory in MB")
    memory_usage = models.FloatField(default=0.0)
    memory_over_allocation = models.FloatField(default=1.0)

    storage = models.PositiveIntegerField(help_text="Storage in MB")
    storage_usage = models.FloatField(default=0.0)
    storage_over_allocation = models.FloatField(default=1.0)

    daemon_version = models.CharField(max_length=50, null=True, blank=True)
    docker_version = models.CharField(max_length=50, null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    daemon_port = models.PositiveIntegerField(default=8080)
    daemon_sftp_port = models.PositiveIntegerField(default=2022)

    @property
    def max_servers(self):
        return self.subscription.plan.max_servers

    @property
    def cpu_percent(self):
        return (self.cpu_usage / (self.cpu_cores * self.cpu_over_allocation)) * 100

    @property
    def memory_percent(self):
        return (self.memory_usage / (self.memory * self.memory_over_allocation)) * 100

    @property
    def storage_percent(self):
        return (self.storage_usage / (self.storage * self.storage_over_allocation)) * 100
    
    
    class Meta:
        unique_together = ('owner', 'name')
        indexes = [
            models.Index(fields=['ip_address']),
        ]

    def __str__(self):
        return f"{self.name} ({self.status})"
