from rest_framework import serializers
from applications.api.servers.serializers import ServerMinimalSerializer
from applications.nodes.models import Node

from rest_framework import serializers
from applications.nodes.models import Node
from applications.api.servers.serializers import ServerMinimalSerializer

class NodeSerializer(serializers.ModelSerializer):
    servers = ServerMinimalSerializer(many=True, read_only=True)

    class Meta:
        model = Node
        fields = "__all__"
        read_only_fields = ['node_uuid', 'owner']
    
    def validate(self, attrs):
        user = self.context['request'].user
        subscription = getattr(user, 'subscription', None)

        if not subscription:
            raise serializers.ValidationError(
                "El usuario no tiene una suscripción activa."
            )

        # Validación solo en creación
        if self.instance is None:
            current_nodes = Node.objects.filter(owner=user).count()
            max_allowed = subscription.plan.max_nodes

            if current_nodes >= max_allowed:
                raise serializers.ValidationError(
                    f"Máximo permitido: {max_allowed} nodos."
                )

        return attrs

