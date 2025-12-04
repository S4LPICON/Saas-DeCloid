from rest_framework import serializers
from applications.servers.models import Server
from rest_framework import serializers

class ServerMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = [
            'server_uuid', 'name', 'status', 'artifact', 'ip_address', 'port'
        ]
        read_only_fields = ['server_uuid', 'owner']

class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = "__all__"
        read_only_fields = ['server_uuid', 'owner']


    def validate(self, attrs):
        user = self.context['request'].user
        subscription = getattr(user, 'subscription', None)

        if self.instance is None:
            if not subscription:
                raise serializers.ValidationError("El usuario no tiene suscripción activa.")

            current_servers = Server.objects.filter(owner=user).count()
            if current_servers >= subscription.plan.max_servers:
                raise serializers.ValidationError(
                    f"Máximos servidores permitidos: {subscription.plan.max_servers}."
                )
        return attrs

