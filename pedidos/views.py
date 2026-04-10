# aqui reexportamos vistas para usarlas desde un solo archivo
from .views.auth import login_view, logout_view, token_status_view, refresh_token_view
from .views.clientes import ClienteListView, crear_cliente, editar_cliente, eliminar_cliente
from .views.productos import ProductoListView, crear_producto, editar_producto, eliminar_producto
from .views.pedidos import PedidoListView, crear_pedido, crear_pedido_con_producto, editar_pedido, eliminar_pedido, detalle_pedido
from .views.detalles import DetallePedidoListView, agregar_detalle, editar_detalle, eliminar_detalle

