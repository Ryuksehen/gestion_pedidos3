# ─────────────────────────────────────────────────────────
# views/auth.py
# Autenticación basada en JWT implementado manualmente (sin dependencias externas).
# Incluye: helpers de codificación, creación y verificación del token,
# y las vistas de login, logout, registro y redirección home.
# ─────────────────────────────────────────────────────────
import base64
import hashlib
import hmac
import json
import time

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


# ─────────────────────────────────────────────────────────
# HELPERS DE CODIFICACIÓN BASE64 URL-SAFE
# El estándar JWT usa base64url (variante sin '+', '/' ni '=' de relleno).
# ─────────────────────────────────────────────────────────
def _b64url_encode(data: bytes) -> str:
    """Codifica bytes a base64 URL-safe sin rellenos."""
    # rstrip(b'=') elimina el padding '=' que no forma parte del estándar JWT
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def _b64url_decode(data: str) -> bytes:
    """Decodifica una cadena base64 URL-safe agregando padding si es necesario."""
    # El JWT no incluye '=', pero urlsafe_b64decode los necesita para funcionar
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


# ─────────────────────────────────────────────────────────
# CREAR TOKEN JWT
# Genera un JWT firmado con HMAC-SHA256 usando el SECRET_KEY del proyecto.
# Estructura: header.payload.signature (cada parte en base64url)
# ─────────────────────────────────────────────────────────
def create_jwt_token(user, expires_in=3600):
    """Crea un JWT simple con HS256, exp y algunos claims básicos."""
    # Cabecera: algoritmo de firma y tipo de token
    header = {'alg': 'HS256', 'typ': 'JWT'}
    # Payload: datos del usuario e instante de expiración (Unix timestamp)
    payload = {
        'user_id':  user.id,
        'username': user.username,
        'exp':      int(time.time()) + expires_in,  # Expira en 1 hora por defecto
    }

    # Codificar header y payload como JSON → base64url
    header_b64  = _b64url_encode(json.dumps(header,  separators=(',', ':')).encode('utf-8'))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))

    # Calcular la firma HMAC-SHA256 sobre "header.payload"
    signature = hmac.new(
        settings.SECRET_KEY.encode('utf-8'),         # Clave secreta de Django
        f'{header_b64}.{payload_b64}'.encode('utf-8'),
        hashlib.sha256,
    ).digest()

    signature_b64 = _b64url_encode(signature)
    # Devolver el token en formato estándar: header.payload.signature
    return f'{header_b64}.{payload_b64}.{signature_b64}'


# ─────────────────────────────────────────────────────────
# VERIFICAR TOKEN JWT
# Valida el formato, la firma y la expiración del token.
# Devuelve el objeto User si todo es correcto, o None si falla.
# ─────────────────────────────────────────────────────────
def verify_jwt_token(token):
    """Verifica el formato, firma, expiración y devuelve el usuario si todo está OK."""
    # Un JWT válido debe tener exactamente 3 partes separadas por '.'
    if not token or token.count('.') != 2:
        return None

    header_b64, payload_b64, signature_b64 = token.split('.')

    try:
        # Decodificar y parsear el header y el payload
        json.loads(_b64url_decode(header_b64))
        payload_raw = json.loads(_b64url_decode(payload_b64))
    except Exception:
        # Si falla la decodificación o el JSON, el token es inválido
        return None

    # Recalcular la firma esperada y compararla con la recibida
    expected_signature = _b64url_encode(
        hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            f'{header_b64}.{payload_b64}'.encode('utf-8'),
            hashlib.sha256,
        ).digest()
    )

    # compare_digest usa comparación en tiempo constante para evitar timing attacks
    if not hmac.compare_digest(expected_signature, signature_b64):
        return None

    # Verificar que el token no haya expirado
    exp = payload_raw.get('exp')
    if not isinstance(exp, int) or exp < int(time.time()):
        return None

    # Extraer el ID del usuario del payload
    user_id = payload_raw.get('user_id')
    if not user_id:
        return None

    try:
        # Buscar y devolver el usuario en la base de datos
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


# ─────────────────────────────────────────────────────────
# VISTA: LOGIN
# Muestra y procesa el formulario de inicio de sesión.
# Tras autenticarse, genera un JWT y lo guarda en una cookie httponly.
# ─────────────────────────────────────────────────────────
def login_view(request):
    """Muestra y procesa el formulario de inicio de sesión.

    - Valida usuario / contraseña.
    - Crea sesión con login(request, user).
    - Genera JWT y pone cookie httponly.
    - Redirige a listar o next.
    """
    # Leer la URL de redirección después del login (si el middleware la puso en ?next=)
    next_url = request.GET.get('next', None)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Validar que ambos campos hayan sido enviados
        if not username or not password:
            context = {'error': 'Ingrese usuario y contraseña.'}
            if next_url:
                context['next'] = next_url
            return render(request, 'pedidos/login.html', context)

        # authenticate() verifica con el backend de autenticación de Django
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # No usamos sesión de Django para login; solo JWT.
            jwt_token = create_jwt_token(user)

            redirect_to = next_url or 'listar'
            response = redirect(redirect_to)
            # Guardar el token en una cookie httponly (no accesible desde JavaScript)
            response.set_cookie(
                'jwt_token',
                jwt_token,
                httponly=True,    # Protege contra XSS
                samesite='Lax',   # Protege parcialmente contra CSRF
                max_age=3600,     # Expira en 1 hora
            )
            return response

        # Credenciales incorrectas: mostrar mensaje de error sin revelar cuál falló
        context = {'error': 'Credenciales inválidas'}
        if next_url:
            context['next'] = next_url
        return render(request, 'pedidos/login.html', context)

    # Para GET, mostrar el formulario de login vacío
    context = {}
    if next_url:
        context['next'] = next_url
    return render(request, 'pedidos/login.html', context)


# ─────────────────────────────────────────────────────────
# VISTA: LOGOUT
# Cierra la sesión de Django y elimina la cookie JWT.
# ─────────────────────────────────────────────────────────
def logout_view(request):
    """Limpiar autenticación y cookie JWT."""
    # Mantener logout(request) para limpiar posibles datos de sesión anteriores.
    logout(request)
    response = redirect('login')
    # Eliminar la cookie JWT para que el navegador no la reenvíe en futuros requests
    response.delete_cookie('jwt_token')
    return response


# ─────────────────────────────────────────────────────────
# VISTA: REGISTRO
# Crea un nuevo usuario con validaciones básicas.
# Usa create_user() para que Django hashee la contraseña correctamente.
# ─────────────────────────────────────────────────────────
def register_view(request):
    """Formulario simple de registro de usuario con validaciones básicas."""
    if request.method == 'POST':
        username         = request.POST.get('username',         '').strip()
        email            = request.POST.get('email',            '').strip()
        password         = request.POST.get('password',         '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        errors = []

        # Validaciones de formato y longitud mínima
        if not username or len(username) < 3:
            errors.append('El nombre de usuario debe tener al menos 3 caracteres.')
        if not email or '@' not in email:
            errors.append('Ingrese un email válido.')
        if not password or len(password) < 6:
            errors.append('La contraseña debe tener al menos 6 caracteres.')
        if password != confirm_password:
            errors.append('Las contraseñas no coinciden.')

        # Verificar unicidad de usuario y email en la base de datos
        UserModel = get_user_model()
        if UserModel.objects.filter(username=username).exists():
            errors.append('El usuario ya existe.')
        if UserModel.objects.filter(email=email).exists():
            errors.append('El email ya está registrado.')

        if errors:
            # Devolver los errores y conservar los datos ya ingresados (excepto contraseña)
            return render(request, 'pedidos/register.html', {
                'errors':   errors,
                'username': username,
                'email':    email,
            })

        # create_user() genera el hash de la contraseña automáticamente (PBKDF2 por defecto)
        user = UserModel.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Redirigir al login para que el usuario acceda con sus nuevas credenciales
        return redirect('login')

    return render(request, 'pedidos/register.html')


# ─────────────────────────────────────────────────────────
# VISTA: HOME
# Redirige automáticamente según el estado de autenticación del usuario.
# ─────────────────────────────────────────────────────────
def home_view(request):
    """Redirige al usuario.

    - si está autenticado, va a la lista de pedidos
    - si no, va a login
    """
    if request.user.is_authenticated:
        return redirect('listar')  # Usuario logueado → panel principal
    return redirect('login')       # Usuario anónimo → pantalla de inicio de sesión


def verify_jwt_token(token):
    """Verifica el formato, firma, expiración y devuelve el usuario si todo está OK."""
    if not token or token.count('.') != 2:
        return None

    header_b64, payload_b64, signature_b64 = token.split('.')

    try:
        json.loads(_b64url_decode(header_b64))
        payload_raw = json.loads(_b64url_decode(payload_b64))
    except Exception:
        return None

    expected_signature = _b64url_encode(
        hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            f'{header_b64}.{payload_b64}'.encode('utf-8'),
            hashlib.sha256,
        ).digest()
    )

    if not hmac.compare_digest(expected_signature, signature_b64):
        return None

    exp = payload_raw.get('exp')
    if not isinstance(exp, int) or exp < int(time.time()):
        return None

    user_id = payload_raw.get('user_id')
    if not user_id:
        return None

    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


def login_view(request):
    """Muestra y procesa el formulario de inicio de sesión.

    - Valida usuario / contraseña.
    - Crea sesión con login(request, user).
    - Genera JWT y pone cookie httponly.
    - Redirige a listar o next.
    """
    next_url = request.GET.get('next', None)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            context = {'error': 'Ingrese usuario y contraseña.'}
            if next_url:
                context['next'] = next_url
            return render(request, 'pedidos/login.html', context)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # No usamos sesión de Django para login; solo JWT.
            jwt_token = create_jwt_token(user)

            redirect_to = next_url or 'listar'
            response = redirect(redirect_to)
            response.set_cookie(
                'jwt_token',
                jwt_token,
                httponly=True,
                samesite='Lax',
                max_age=3600,
            )
            return response

        context = {'error': 'Credenciales inválidas'}
        if next_url:
            context['next'] = next_url
        return render(request, 'pedidos/login.html', context)

    context = {}
    if next_url:
        context['next'] = next_url
    return render(request, 'pedidos/login.html', context)


def logout_view(request):
    """Limpiar autenticación y cookie JWT."""
    # Mantener logout(request) para limpiar posibles datos de sesión anteriores.
    logout(request)
    response = redirect('login')
    response.delete_cookie('jwt_token')
    return response


def register_view(request):
    """Formulario simple de registro de usuario con validaciones básicas."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        errors = []

        # validaciones simples recomendadas
        if not username or len(username) < 3:
            errors.append('El nombre de usuario debe tener al menos 3 caracteres.')
        if not email or '@' not in email:
            errors.append('Ingrese un email válido.')
        if not password or len(password) < 6:
            errors.append('La contraseña debe tener al menos 6 caracteres.')
        if password != confirm_password:
            errors.append('Las contraseñas no coinciden.')

        # comprobación de unicidad en DB
        UserModel = get_user_model()
        if UserModel.objects.filter(username=username).exists():
            errors.append('El usuario ya existe.')
        if UserModel.objects.filter(email=email).exists():
            errors.append('El email ya está registrado.')

        if errors:
            return render(request, 'pedidos/register.html', {
                'errors': errors,
                'username': username,
                'email': email,
            })

        # creación segura usando create_user (hash de contraseña)
        user = UserModel.objects.create_user(username=username, email=email, password=password)
        user.save()

        # envío a login para acceso inmediato
        return redirect('login')

    return render(request, 'pedidos/register.html')


def home_view(request):
    """Redirige al usuario.

    - si está autenticado, va a la lista de pedidos
    - si no, va a login
    """
    if request.user.is_authenticated:
        return redirect('listar')
    return redirect('login')
