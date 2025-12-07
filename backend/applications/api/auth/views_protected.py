from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Aquí luego vas a leerlo de la BD, pero por ahora lo puedes hardcodear
        fake_plan = {
            "name": "FREE",
            "nodes": 1,
            "images": 1,
            "price": 0,
        }

        usage = {
            "nodes_used": 0,
            "images_used": 0,
        }

        return Response({
            "id": user.id,
            "email": user.email,
            "plan": fake_plan,
            "usage": usage,
        })
