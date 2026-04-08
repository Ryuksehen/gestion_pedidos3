# aqui importamos vistas de acceso
from .auth import login_view, logout_view, register_view, home_view
# aqui importamos vistas de clientes
from .clientes import ClienteListView, crear_cliente, editar_cliente, eliminar_cliente
# aqui importamos vistas de productos
from .productos import ProductoListView, crear_producto, editar_producto, eliminar_producto
# aqui importamos vistas de pedidos
from .pedidos import PedidoListView, crear_pedido, editar_pedido, eliminar_pedido, detalle_pedido
# aqui importamos vistas de detalles de pedidos
from .detalles import DetallePedidoListView, agregar_detalle, editar_detalle, eliminar_detalle

# aqui definimos lo que se exporta al importar este paquete
__all__ = [
    'login_view', 'logout_view', 'register_view', 'home_view',
    'ClienteListView', 'crear_cliente', 'editar_cliente', 'eliminar_cliente',
    'ProductoListView', 'crear_producto', 'editar_producto', 'eliminar_producto',
    'PedidoListView', 'crear_pedido', 'editar_pedido', 'eliminar_pedido', 'detalle_pedido',
    'DetallePedidoListView', 'agregar_detalle', 'editar_detalle', 'eliminar_detalle',
]

