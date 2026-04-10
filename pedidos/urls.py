from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from . import reportes
from .views.api import (
    ClienteViewSet,
    ProductoViewSet,
    PedidoViewSet,
    DetallePedidoViewSet,
    ApiLoginView,
    ApiLogoutView,
    ApiRegistroView,
)


# aqui registramos rutas automaticas del crud rest
router = DefaultRouter()
router.register(r'api/clientes', ClienteViewSet, basename='api-clientes')
router.register(r'api/productos', ProductoViewSet, basename='api-productos')
router.register(r'api/pedidos', PedidoViewSet, basename='api-pedidos')
router.register(r'api/detalles', DetallePedidoViewSet, basename='api-detalles')


# aqui juntamos todas las rutas del modulo pedidos
urlpatterns = [
    # aqui van las rutas del crud de pedidos
    path('',                       views.home_view,               name='home'),
    path('listar/',                views.PedidoListView.as_view(), name='listar'),
    path('crear/',                 views.crear_pedido,             name='crear'),
    path('crear-con-producto/',    views.crear_pedido_con_producto, name='crear_con_producto'),
    path('editar/<int:pk>/',       views.editar_pedido,            name='editar'),
    path('eliminar/<int:pk>/',     views.eliminar_pedido,          name='eliminar'),
    path('detalle/<int:pk>/',      views.detalle_pedido,           name='detalle'),

    # aqui van las rutas de acceso y sesion
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('registro/', views.register_view, name='register'),
    path('api/auth/token-status/', views.token_status_view, name='token_status'),
    path('api/auth/refresh/', views.refresh_token_view, name='token_refresh'),

    # aqui van las rutas de clientes
    path('clientes/',                   views.ClienteListView.as_view(), name='listar_clientes'),
    path('clientes/crear/',             views.crear_cliente,             name='crear_cliente'),
    path('clientes/editar/<int:pk>/',   views.editar_cliente,            name='editar_cliente'),
    path('clientes/eliminar/<int:pk>/', views.eliminar_cliente,          name='eliminar_cliente'),

    # aqui van las rutas de productos
    path('productos/',                   views.ProductoListView.as_view(), name='listar_productos'),
    path('productos/crear/',             views.crear_producto,             name='crear_producto'),
    path('productos/editar/<int:pk>/',   views.editar_producto,            name='editar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto,          name='eliminar_producto'),

    # aqui van las rutas de detalle de pedidos
    path('detalles/',                           views.DetallePedidoListView.as_view(), name='listar_detalles'),
    path('pedido/<int:pedido_id>/agregar/',     views.agregar_detalle,                 name='agregar_detalle'),
    path('detalle/editar/<int:pk>/',            views.editar_detalle,                  name='editar_detalle'),
    path('detalle/eliminar/<int:pk>/',          views.eliminar_detalle,                name='eliminar_detalle'),

    # aqui van las rutas para exportar reportes
    path('exportar/pedidos/pdf/',   reportes.exportar_pedidos_pdf),
    path('exportar/clientes/pdf/',  reportes.exportar_clientes_pdf),
    path('exportar/productos/pdf/', reportes.exportar_productos_pdf),
    path('exportar/detalles/pdf/',  reportes.exportar_detalles_pdf),
    path('exportar/todo/excel/',     reportes.exportar_todo_excel),
    path('exportar/detalles/excel/', reportes.exportar_detalles_excel),
    path('exportar/clientes/json/',              reportes.exportar_clientes_json),
    path('exportar/productos/json/',             reportes.exportar_productos_json),
    path('exportar/pedidos/detallado/json/',     reportes.exportar_pedidos_detallado_json),

    # aqui van rutas de autenticacion api jwt
    path('api/auth/login/', ApiLoginView.as_view(), name='api_login'),
    path('api/auth/logout/', ApiLogoutView.as_view(), name='api_logout'),
    path('api/auth/registro/', ApiRegistroView.as_view(), name='api_registro'),
]

# aqui anexamos rutas del router rest
urlpatterns += router.urls
