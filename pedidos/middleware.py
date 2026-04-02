from django.contrib.auth import get_user_model

from .views.auth import verify_jwt_token


# ───────────────────────────────────────────────────────────────
# MIDDLEWARE: JWTAuthenticationMiddleware
# Se ejecuta en CADA request antes de que llegue a la vista.
# Permite autenticar usuarios mediante un token JWT almacenado como:
#   - Cookie httponly 'jwt_token'  (navegador web)
#   - Header 'Authorization: Bearer <token>'  (clientes API)
# Si el usuario ya tiene sesión activa de Django, el middleware no interfiere.
# ───────────────────────────────────────────────────────────────
class JWTAuthenticationMiddleware:
    """Middleware que valida usuario por cookie o Authorization Bearer JWT.

    - Si ya está logueado por sesión, no cambia.
    - Si está anónimo y tiene JWT válido, se asocia el usuario.
    """

    def __init__(self, get_response):
        # get_response es el siguiente eslabón en la cadena de middlewares o la vista destino
        self.get_response = get_response

    def __call__(self, request):
        # Si Django ya reconoce al usuario autenticado, no es necesario procesar el token
        if request.user.is_authenticated:
            return self.get_response(request)

        # Intentar obtener el token JWT desde la cookie del navegador
        token = request.COOKIES.get('jwt_token')
        if not token:
            # Si no hay cookie, buscar el token en el encabezado Authorization
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                # Extraer solo el token (omitir el prefijo "Bearer ")
                token = auth_header[7:]

        if token:
            # Validar la firma, fecha de expiración y existencia del usuario
            user = verify_jwt_token(token)
            if user:
                # Asociar el usuario al request para que las vistas lo vean como autenticado
                request.user = user

        return self.get_response(request)
