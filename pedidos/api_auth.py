from rest_framework import authentication, exceptions

from .views.auth import verify_jwt_token


# aqui permitimos autenticacion JWT para la api rest
class JwtApiAuthentication(authentication.BaseAuthentication):
    """Autentica por header Authorization Bearer o por cookie jwt_token."""

    def authenticate(self, request):
        token = None
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = request.COOKIES.get('jwt_token')

        if not token:
            return None

        user = verify_jwt_token(token)
        if not user:
            raise exceptions.AuthenticationFailed('Token JWT invalido o vencido.')

        return (user, None)
