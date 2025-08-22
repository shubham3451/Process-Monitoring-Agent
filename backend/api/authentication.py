from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class AgentAPIKeyAuthentication(BaseAuthentication):
    """
    Accepts X-API-Key: <key> or Authorization: ApiKey <key>
    Allows safe methods (GET/OPTIONS) without key.

    """
    
    def authenticate(self, request):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return (None, None) 

        key = request.headers.get("X-API-Key")
        if not key:
            auth = request.headers.get("Authorization", "")
            if auth.startswith("ApiKey "):
                key = auth.split(" ", 1)[1].strip()

        if not key:
            raise AuthenticationFailed("Missing API key.")

        required = settings.AGENT_API_KEY
        if key != required:
            raise AuthenticationFailed("Invalid API key.")

        return (None, None)
