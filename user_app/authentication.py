
from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that uses cookies instead of Authorization header.
    """
    def authenticate(self, request):
        """
        Authenticate the request by getting the token from cookies.
        """
        access_token = request.COOKIES.get("access_token")
        if not access_token:
            return None

        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except Exception:
            return None
