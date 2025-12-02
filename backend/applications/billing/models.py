from django.db import models
from django.contrib.auth.models import User

class Plan(models.Model):
    
    """
    Define un plan de suscripción con límites de recursos y precio.
    """
    
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    max_nodes = models.PositiveIntegerField(default=1)
    max_artifacts = models.PositiveIntegerField(default=1)
    max_servers = models.PositiveIntegerField(default=1)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


    
    
class UserSubscription(models.Model):
    """
    Representa la suscripción activa de un usuario a un plan.
    """
    
    owner = models.OneToOneField(User, on_delete=models.PROTECT, related_name="subscription")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.owner.username} - {self.plan.name}"
