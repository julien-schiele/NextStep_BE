# apps/utils/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication

class JWTAuthenticationExcludeOptions(JWTAuthentication):
    def authenticate(self, request):
        if request.method == "OPTIONS":
            return None
        return super().authenticate(request)