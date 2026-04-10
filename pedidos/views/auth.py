import base64
import hashlib
import hmac
import json
import re
import time

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST


# aqui convertimos bytes a base64 para el token
def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


# aqui recuperamos bytes desde base64 del token
def _b64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


# aqui armamos el jwt para guardar sesion
# expires_in define cuantos segundos vive el token
def create_jwt_token(user, expires_in=3600):
    header = {'alg': 'HS256', 'typ': 'JWT'}
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': int(time.time()) + expires_in,
    }

    header_b64 = _b64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))

    signature = hmac.new(
        settings.SECRET_KEY.encode('utf-8'),
        f'{header_b64}.{payload_b64}'.encode('utf-8'),
        hashlib.sha256,
    ).digest()

    signature_b64 = _b64url_encode(signature)
    return f'{header_b64}.{payload_b64}.{signature_b64}'


# aqui validamos que el jwt sea real y vigente
def verify_jwt_token(token):
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


# aqui obtenemos payload del token para conocer su expiracion
def get_jwt_payload(token, validate_exp=True):
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
    if not isinstance(exp, int):
        return None

    if validate_exp and exp < int(time.time()):
        return None

    return payload_raw


# aqui manejamos ingreso con usuario y clave
def login_view(request):
    next_url = request.GET.get('next')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        next_url = request.POST.get('next') or next_url

        if not username or not password:
            context = {'error': 'Ingrese usuario y contrasena.', 'active_form': 'login'}
            if next_url:
                context['next'] = next_url
            return render(request, 'pedidos/login.html', context)

        if len(username) < 3:
            context = {'error': 'El usuario debe tener al menos 3 caracteres.', 'active_form': 'login'}
            if next_url:
                context['next'] = next_url
            return render(request, 'pedidos/login.html', context)

        if len(password) < 6:
            context = {'error': 'La contrasena debe tener al menos 6 caracteres.', 'active_form': 'login'}
            if next_url:
                context['next'] = next_url
            return render(request, 'pedidos/login.html', context)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # tiempo de vida del token leido desde settings
            lifetime = int(getattr(settings, 'JWT_ACCESS_TOKEN_LIFETIME_SECONDS', 3600))
            jwt_token = create_jwt_token(user, expires_in=lifetime)
            redirect_to = next_url or 'listar'
            response = redirect(redirect_to)
            response.set_cookie(
                'jwt_token',
                jwt_token,
                httponly=True,
                samesite='Lax',
                # la cookie vive lo mismo que el token
                max_age=lifetime,
            )
            return response

        context = {'error': 'Credenciales invalidas.', 'active_form': 'login'}
        if next_url:
            context['next'] = next_url
        return render(request, 'pedidos/login.html', context)

    context = {'active_form': 'login'}
    if next_url:
        context['next'] = next_url
    return render(request, 'pedidos/login.html', context)


# aqui cerramos sesion y borramos cookie jwt
def logout_view(request):
    logout(request)
    response = redirect('login')
    response.delete_cookie('jwt_token')
    return response


# aqui registramos usuarios nuevos con validaciones simples
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        errors = []

        if not username or len(username) < 3:
            errors.append('El nombre de usuario debe tener al menos 3 caracteres.')
        if username and not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('El usuario solo puede tener letras, numeros y guion bajo.')

        if not email or '@' not in email:
            errors.append('Ingrese un email valido.')
        elif '.' not in email.split('@')[-1]:
            errors.append('Ingrese un email valido.')

        if not password or len(password) < 6:
            errors.append('La contrasena debe tener al menos 6 caracteres.')
        if password and not re.search(r'[A-Za-z]', password):
            errors.append('La contrasena debe incluir al menos una letra.')
        if password and not re.search(r'[0-9]', password):
            errors.append('La contrasena debe incluir al menos un numero.')

        if password != confirm_password:
            errors.append('Las contrasenas no coinciden.')

        UserModel = get_user_model()
        if UserModel.objects.filter(username=username).exists():
            errors.append('El usuario ya existe.')
        if UserModel.objects.filter(email=email).exists():
            errors.append('El email ya esta registrado.')

        if errors:
            return render(request, 'pedidos/login.html', {
                'active_form': 'register',
                'errors': errors,
                'username': username,
                'email': email,
            })

        user = UserModel.objects.create_user(username=username, email=email, password=password)
        user.save()
        return redirect('login')

    return render(request, 'pedidos/login.html', {'active_form': 'register'})


# aqui enviamos al inicio correcto segun estado de sesion
def home_view(request):
    if request.user.is_authenticated:
        return redirect('listar')
    return redirect('login')


# aqui devolvemos segundos restantes del token para cuenta regresiva
@require_GET
def token_status_view(request):
    token = request.COOKIES.get('jwt_token')
    payload = get_jwt_payload(token, validate_exp=False)

    if not payload:
        return JsonResponse({'autenticado': False}, status=401)

    exp = payload.get('exp', 0)
    ahora = int(time.time())
    # segundos restantes reales para expirar token
    expires_in = max(0, int(exp) - ahora)

    return JsonResponse(
        {
            'autenticado': expires_in > 0,
            'expires_in': expires_in,
            # tiempo previo para mostrar alerta de expiracion
            'warning_seconds': int(getattr(settings, 'JWT_EXPIRY_WARNING_SECONDS', 120)),
            # limite total de inactividad permitido
            'inactivity_seconds': int(getattr(settings, 'JWT_INACTIVITY_TIMEOUT_SECONDS', 900)),
            # segundos de aviso previo antes de cerrar por inactividad
            'inactivity_warning_seconds': int(getattr(settings, 'JWT_INACTIVITY_WARNING_SECONDS', 60)),
        }
    )


# aqui renovamos token antes de que expire
@require_POST
def refresh_token_view(request):
    token = request.COOKIES.get('jwt_token')
    payload = get_jwt_payload(token, validate_exp=True)

    if not payload:
        return JsonResponse({'mensaje': 'Token invalido o vencido.'}, status=401)

    user_id = payload.get('user_id')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'mensaje': 'Usuario no encontrado.'}, status=401)

    # al renovar, se vuelve a usar la duracion oficial del token
    lifetime = int(getattr(settings, 'JWT_ACCESS_TOKEN_LIFETIME_SECONDS', 3600))
    new_token = create_jwt_token(user, expires_in=lifetime)

    response = JsonResponse({'mensaje': 'Token renovado.', 'expires_in': lifetime})
    response.set_cookie(
        'jwt_token',
        new_token,
        httponly=True,
        samesite='Lax',
        max_age=lifetime,
    )
    return response
