# Guia API + Postman (JWT)

Este documento explica:
1. Donde se cambia la duracion del token JWT.
2. Como obtener y usar el token en Postman.
3. Como crear/usar usuarios para login desde Postman.
4. Todos los endpoints para GET, POST, PUT y PATCH.

## 1) Base URL

http://127.0.0.1:8000

## 2) Donde modificar el tiempo de duracion del token

En este proyecto el JWT es manual (no usa SimpleJWT), y la configuracion se cambia en UN solo lugar:

1. Archivo: proyecto_pedidos/settings.py
2. Variables:
  - JWT_ACCESS_TOKEN_LIFETIME_SECONDS
  - JWT_EXPIRY_WARNING_SECONDS
  - JWT_INACTIVITY_TIMEOUT_SECONDS
  - JWT_INACTIVITY_WARNING_SECONDS

Importante:
1. NO necesitas cambiar auth.py ni api.py cada vez.
2. Esos archivos ya leen los valores de settings automaticamente.
3. Si cambias tiempos, reinicia servidor y vuelve a iniciar sesion.

Ejemplo rapido de prueba:
- JWT_ACCESS_TOKEN_LIFETIME_SECONDS = 300
- JWT_EXPIRY_WARNING_SECONDS = 60
- JWT_INACTIVITY_TIMEOUT_SECONDS = 180
- JWT_INACTIVITY_WARNING_SECONDS = 30


## 2.1) Login y registro usan URL diferente? (respuesta corta: SI)

Si, son endpoints distintos y cada uno cumple una funcion diferente:

1. Obtener token (login): POST /api/auth/login/
2. Registrar usuario: POST /api/auth/registro/
3. Cerrar sesion/token: POST /api/auth/logout/
4. Ver estado del token web: GET /api/auth/token-status/
5. Renovar token web: POST /api/auth/refresh/

Resumen simple:
1. Registro crea el usuario.
2. Login valida usuario+clave y te devuelve token.
3. Sin login no hay token para Authorization Bearer.

## 3) Como obtener el token en Postman

Endpoint:
- POST /api/auth/login/

Body JSON:

```json
{
  "username": "admin",
  "password": "123456"
}
```

Respuesta esperada (ejemplo):

```json
{
  "mensaje": "Login correcto.",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "usuario": {
    "id": 1,
    "username": "admin",
    "email": "admin@correo.com"
  }
}
```

Como usarlo en las demas requests:

1. Ve a la pestana Headers.
2. Agrega:
   - Key: Authorization
   - Value: Bearer TU_TOKEN

Tambien funciona por cookie jwt_token, pero en Postman normalmente se usa mas el header Authorization.

## 4) Usuarios de login desde Postman (crear, usar y editar)

### 4.1 Crear usuario (registro)

Endpoint:
- POST /api/auth/registro/

Body JSON:

```json
{
  "username": "usuario1",
  "email": "usuario1@correo.com",
  "password": "clave123"
}
```

### 4.2 Seleccionar usuario para login

No hay un endpoint para "seleccionar" usuario de forma visual.
En Postman, seleccionas el usuario escribiendo su username y password en /api/auth/login/.

### 4.3 Editar usuarios de login

Actualmente NO existe endpoint API para editar usuarios (username/email/password) desde Postman.

Opciones actuales:
1. Editarlo desde Django Admin: /admin/
2. Crear uno nuevo con /api/auth/registro/

Si quieres, luego puedo agregarte endpoints de usuarios para GET, POST, PUT, PATCH y DELETE.

## 5) Endpoints disponibles para Postman

## 5.1 Autenticacion

1. POST /api/auth/login/
2. POST /api/auth/registro/
3. POST /api/auth/logout/
4. GET /api/auth/token-status/
5. POST /api/auth/refresh/

## 5.2 Clientes

1. GET /api/clientes/
2. POST /api/clientes/
3. GET /api/clientes/{id}/
4. PUT /api/clientes/{id}/
5. PATCH /api/clientes/{id}/
6. DELETE /api/clientes/{id}/

Body ejemplo POST/PUT:

```json
{
  "nombre": "Juan Perez",
  "correo": "juan@correo.com",
  "direccion": "Av. Central 123",
  "telefono": "987654321"
}
```

Body ejemplo PATCH:

```json
{
  "telefono": "999888777"
}
```

## 5.3 Productos

1. GET /api/productos/
2. POST /api/productos/
3. GET /api/productos/{id}/
4. PUT /api/productos/{id}/
5. PATCH /api/productos/{id}/
6. DELETE /api/productos/{id}/

Body ejemplo POST/PUT:

```json
{
  "nombre": "Teclado mecanico",
  "precio": "120.50",
  "stock": 20
}
```

Body ejemplo PATCH:

```json
{
  "stock": 15
}
```

## 5.4 Pedidos

1. GET /api/pedidos/
2. POST /api/pedidos/
3. GET /api/pedidos/{id}/
4. PUT /api/pedidos/{id}/
5. PATCH /api/pedidos/{id}/
6. DELETE /api/pedidos/{id}/

Body ejemplo POST/PUT:

```json
{
  "cliente": 1,
  "fecha": "2026-04-08",
  "estado": "pendiente"
}
```

Body ejemplo PATCH:

```json
{
  "estado": "enviado"
}
```

## 5.5 Detalles de pedido

1. GET /api/detalles/
2. POST /api/detalles/
3. GET /api/detalles/{id}/
4. PUT /api/detalles/{id}/
5. PATCH /api/detalles/{id}/
6. DELETE /api/detalles/{id}/

Body ejemplo POST/PUT:

```json
{
  "pedido": 1,
  "producto": 1,
  "cantidad": 2
}
```

Body ejemplo PATCH:

```json
{
  "cantidad": 3
}
```

Notas:
1. subtotal es solo lectura, lo calcula el sistema.
2. Si la cantidad supera el stock, la API devuelve error.
3. Al crear/editar/eliminar detalles, el stock se ajusta automaticamente.

## 6) Flujo recomendado en Postman (paso a paso)

1. Registrar usuario en /api/auth/registro/ (si aun no existe).
2. Hacer login en /api/auth/login/.
3. Copiar token de la respuesta.
4. Agregar header Authorization: Bearer TU_TOKEN.
5. Probar CRUD (GET/POST/PUT/PATCH/DELETE) en clientes, productos, pedidos y detalles.
6. Si quieres renovar sesion web, usar /api/auth/refresh/.
