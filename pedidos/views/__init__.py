# ─────────────────────────────────────────────────────────
# views/__init__.py
# Re-exporta todas las vistas desde sus módulos individuales
# para que urls.py pueda importarlas con un único 'from . import views'.
# ─────────────────────────────────────────────────────────

# Vistas de autenticación: login, logout, registro y redirección home
from .auth import login_view, logout_view, register_view, home_view

# Vistas CRUD de clientes
from .clientes import ClienteListView, crear_cliente, editar_cliente, eliminar_cliente

# Vistas CRUD de productos
from .productos import ProductoListView, crear_producto, editar_producto, eliminar_producto

# Vistas CRUD de pedidos + vista de detalle individual
from .pedidos import PedidoListView, crear_pedido, editar_pedido, eliminar_pedido, detalle_pedido

# Vistas CRUD de líneas de detalle (productos dentro de un pedido)
from .detalles import DetallePedidoListView, agregar_detalle, editar_detalle, eliminar_detalle

# __all__ declara explícitamente qué nombres se exportan al hacer 'from views import *'
__all__ = [
    'login_view', 'logout_view', 'register_view', 'home_view',
    'ClienteListView', 'crear_cliente', 'editar_cliente', 'eliminar_cliente',
    'ProductoListView', 'crear_producto', 'editar_producto', 'eliminar_producto',
    'PedidoListView', 'crear_pedido', 'editar_pedido', 'eliminar_pedido', 'detalle_pedido',
    'DetallePedidoListView', 'agregar_detalle', 'editar_detalle', 'eliminar_detalle',
]
