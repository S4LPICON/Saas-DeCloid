from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from applications.nodes.models import Node

class Command(BaseCommand):
    help = "Marca nodos offline si no enviaron heartbeat reciente"

    def handle(self, *args, **kwargs):
        limit = timezone.now() - timedelta(seconds=30)

        offline_nodes = Node.objects.filter(
            is_online=True,
            last_heartbeat__lt=limit
        )

        count = offline_nodes.count()
        offline_nodes.update(is_online=False)

        self.stdout.write(f"Nodos marcados offline: {count}")
