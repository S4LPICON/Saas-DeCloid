from rest_framework import serializers
from applications.nodes.models import Node

class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = "__all__"
        read_only_fields = ['node_uuid', 'owner']
    
    def validate(self, attrs):
        user = self.context['request'].user
        subscription = attrs.get('subscription')
        
        if self.instance is None and subscription:  # Solo para creación
            current_nodes = Node.objects.filter(owner=user).count()
            if current_nodes >= subscription.plan.max_nodes:
                raise serializers.ValidationError(
                    f"Maximos nodos: ({subscription.plan.max_nodes})."
                )
        return attrs
