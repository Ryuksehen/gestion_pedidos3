# Guia rapida: JWT y API REST (Postman)

## 1) Ahora que tiene el proyecto?

Este proyecto ahora tiene dos capas:

- App web Django (HTML) para uso en navegador.
- API REST (JSON) bajo el prefijo /api/.

Asi puedes usar el sistema desde formularios web o desde Postman/Frontend externo.

---

## 2) Como funciona el JWT aqui

El JWT es propio (implementado en codigo del proyecto), con firma HS256.

Flujo simple:

1. Haces login por API en /api/auth/login/.
2. El servidor valida usuario y password.
3. Si es correcto, responde un token y tambien lo guarda en cookie httponly jwt_token.
4. En cada request de API, se acepta token por:
   - Header Authorization: Bearer <token>
   - o cookie jwt_token
5. Si el token es valido y no vencio, la API deja pasar la peticion.

Archivos clave:

- pedidos/views/auth.py
  - create_jwt_token(...)
  - verify_jwt_token(...)
- pedidos/api_auth.py
  - JwtApiAuthentication
- pedidos/views/api.py
  - ApiLoginView, ApiLogoutView, ApiRegistroView
- proyecto_pedidos/settings.py
  - REST_FRAMEWORK con autenticacion JWT

---

## 3) Base URL

http://127.0.0.1:8000

---

## 4) Endpoints API REST (JSON)

## Auth API

- POST /api/auth/login/
  - body JSON:
    - username
    - password

- POST /api/auth/registro/
  - body JSON:
    - username
    - email
    - password

- POST /api/auth/logout/
  - requiere JWT

## Clientes API

- GET /api/clientes/
- POST /api/clientes/
- GET /api/clientes/{id}/
- PUT /api/clientes/{id}/
- PATCH /api/clientes/{id}/
- DELETE /api/clientes/{id}/

Campos JSON:
- nombre
- correo
- direccion
- telefono

## Productos API

- GET /api/productos/
- POST /api/productos/
- GET /api/productos/{id}/
- PUT /api/productos/{id}/
- PATCH /api/productos/{id}/
- DELETE /api/productos/{id}/

Campos JSON:
- nombre
- precio
- stock

## Pedidos API

- GET /api/pedidos/
- POST /api/pedidos/
- GET /api/pedidos/{id}/
- PUT /api/pedidos/{id}/
- PATCH /api/pedidos/{id}/
- DELETE /api/pedidos/{id}/

Campos JSON:
- cliente (id del cliente)
- fecha (YYYY-MM-DD)
- estado (pendiente|enviado|entregado)

## Detalles API

- GET /api/detalles/
- POST /api/detalles/
- GET /api/detalles/{id}/
- PUT /api/detalles/{id}/
- PATCH /api/detalles/{id}/
- DELETE /api/detalles/{id}/

Campos JSON:
- pedido (id del pedido)
- producto (id del producto)
- cantidad

Nota:
- subtotal es de solo lectura (lo calcula el sistema).
- al crear/editar/eliminar detalles, se ajusta stock automaticamente.

---

## 5) Como probar en Postman

1. Login:
   - POST /api/auth/login/
   - Body -> raw -> JSON:
     {
       "username": "tu_usuario",
       "password": "tu_clave"
     }

2. Copia el token de la respuesta.

3. En las demas requests agrega header:
   - Authorization: Bearer <token>

4. Prueba CRUD, por ejemplo:
   - GET /api/clientes/
   - POST /api/productos/
   - PATCH /api/pedidos/1/

---

## 6) Endpoints web antiguos (siguen funcionando)

Tus rutas HTML no se eliminaron. Siguen activas para navegador:

- /login/
- /listar/
- /clientes/
- /productos/
- /detalles/
- /exportar/... (pdf/excel/json)
