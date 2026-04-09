# Guia API + Postman (JWT)

Este documento explica:
1. Donde se cambia la duracion del token JWT.
2. Como obtener y usar el token en Postman.
3. Como crear/usar usuarios para login desde Postman.
4. Todos los endpoints para GET, POST, PUT y PATCH.

## 1) Base URL

http://127.0.0.1:8000

## 2) Donde modificar el tiempo de duracion del token

En este proyecto el JWT es manual (no usa SimpleJWT), por eso la duracion se cambia en codigo:

1. Archivo: pedidos/views/auth.py
2. Funcion: create_jwt_token(user, expires_in=3600)
3. Clave: el parametro expires_in esta en segundos.

Ejemplo rapido:
- 3600 = 1 hora
- 7200 = 2 horas
- 1800 = 30 minutos

Ademas, para que la cookie coincida con ese tiempo, ajusta tambien max_age=3600 en:

1. pedidos/views/auth.py (en login_view)
2. pedidos/views/api.py (en ApiLoginView)

Recomendacion:
- Usa el mismo valor para expires_in y max_age, para evitar que el token y la cookie se desincronicen.

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
