from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from applications.nodes.models import Node
from applications.api.nodes.serializers import NodeSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def nodes_by_owner(request, owner_id):
    nodes = Node.objects.filter(owner_id=owner_id)

    if not nodes.exists():
        return Response(
            {"error": "El usuario no tiene nodos registrados"},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response(NodeSerializer(nodes, many=True).data)
