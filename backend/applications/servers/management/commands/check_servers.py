from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from applications.nodes.models import Node
from applications.servers.models import Server

class Command(BaseCommand):
    help = "Marca servers offline si no enviaron heartbeat reciente"

    def handle(self, *args, **kwargs):
        limit = timezone.now() - timedelta(seconds=30)

        offline_servers = Server.objects.filter(
            is_online=True,
            last_heartbeat__lt=limit
        )

        count = offline_servers.count()
        offline_servers.update(is_online=False)

        self.stdout.write(f"Servers marcados offline: {count}")
