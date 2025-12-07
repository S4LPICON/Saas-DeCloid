# applications/auth/orchestrator_auth.py

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class OrchestratorAuthentication(BaseAuthentication):
    def authenticate(self, request):
        key = request.headers.get("X-Orchestrator-Key")
        if not key or key != settings.ORCHESTRATOR_API_KEY:
            raise AuthenticationFailed("Invalid Orchestrator Key")

        # No hay usuario real → responde un user dummy
        return (None, None)
