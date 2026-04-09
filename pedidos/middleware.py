from django.shortcuts import redirect
from django.urls import reverse

from .views.auth import verify_jwt_token


# aqui leemos jwt en cada request para dejar usuario activo
class JWTAuthenticationMiddleware:
    """Middleware que valida usuario por cookie o Authorization Bearer JWT.

    - Si ya está logueado por sesión, no cambia.
    - Si está anónimo y tiene JWT válido, se asocia el usuario.
    """

    # aqui guardamos el siguiente paso del middleware
    def __init__(self, get_response):
        self.get_response = get_response

    # aqui procesamos la peticion y validamos token
    def __call__(self, request):
        if request.user.is_authenticated:
            return self.get_response(request)

        token = request.COOKIES.get('jwt_token')
        if not token:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]

        if token:
            user = verify_jwt_token(token)
            if user:
                request.user = user
            else:
                ruta = request.path
                es_api = ruta.startswith('/api/')
                rutas_publicas = {
                    reverse('login'),
                    reverse('logout'),
                    reverse('register'),
                }

                if not es_api and ruta not in rutas_publicas:
                    response = redirect(f"{reverse('login')}?sesion=seguridad")
                    response.delete_cookie('jwt_token')
                    return response

        return self.get_response(request)

