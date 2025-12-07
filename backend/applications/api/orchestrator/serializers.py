from rest_framework import serializers
from django.contrib.auth import get_user_model
from applications.servers.models import Server
from applications.nodes.models import Node
from applications.artifacts.models import Artifact

User = get_user_model()

class ServerOrchestratorSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    node = serializers.PrimaryKeyRelatedField(queryset=Node.objects.all())
    artifact = serializers.PrimaryKeyRelatedField(queryset=Artifact.objects.all())

    class Meta:
        model = Server
        fields = [
            'name',
            'ip_address',
            'port',
            'node',
            'artifact',
            'owner' 
            # Agrega 'container_id' si tu modelo lo tiene, suele ser útil que el orquestador lo mande
        ]

    def create(self, validated_data):
        # Lógica estándar de creación
        return Server.objects.create(**validated_data)
    
    def validate(self, attrs):
        # 1. Obtenemos al DUEÑO REAL desde los datos enviados (payload)
        # Como es un PrimaryKeyRelatedField, DRF ya lo convirtió en una instancia de User.
        real_owner = attrs.get('owner')

        if not real_owner:
            raise serializers.ValidationError("Se requiere especificar un owner.")

        # 2. Buscamos la suscripción de ESE usuario, no del bot
        subscription = getattr(real_owner, 'subscription', None)

        # Validación A: ¿Tiene plan?
        if not subscription:
            raise serializers.ValidationError(f"El usuario {real_owner.username} no tiene una suscripción activa.")

        # Validación B: ¿Llegó al límite?
        # Contamos los servidores que pertenecen al DUEÑO REAL
        current_servers = Server.objects.filter(owner=real_owner).count()
        
        # OJO: Si es una edición (update), excluimos el servidor actual del conteo
        if self.instance: 
            # Si estamos editando, no sumamos
            pass 
        else:
            # Si estamos creando, verificamos el límite
            if current_servers >= subscription.plan.max_servers:
                raise serializers.ValidationError(
                    f"El usuario ha alcanzado el límite de su plan ({subscription.plan.max_servers} servidores)."
                )

        return attrs