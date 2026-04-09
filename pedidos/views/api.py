from django.contrib.auth import logout
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from pedidos.models import Cliente, Producto, Pedido, DetallePedido
from pedidos.serializers import (
    ClienteSerializer,
    ProductoSerializer,
    PedidoSerializer,
    DetallePedidoSerializer,
    ApiLoginSerializer,
    ApiRegistroSerializer,
)
from .auth import create_jwt_token


# aqui va crud api de clientes
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by('id')
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    # aqui evitamos borrar cliente con pedidos
    def destroy(self, request, *args, **kwargs):
        cliente = self.get_object()
        if cliente.pedido_set.exists():
            return Response(
                {'detalle': 'No puedes eliminar este cliente porque tiene pedidos asociados.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


# aqui va crud api de productos
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by('id')
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]

    # aqui evitamos borrar producto con detalles
    def destroy(self, request, *args, **kwargs):
        producto = self.get_object()
        if producto.detallepedido_set.exists():
            return Response(
                {'detalle': 'No puedes eliminar este producto porque esta asociado a pedidos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


# aqui va crud api de pedidos
class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().order_by('id')
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

    # aqui evitamos borrar pedido con detalles
    def destroy(self, request, *args, **kwargs):
        pedido = self.get_object()
        if pedido.detallepedido_set.exists():
            return Response(
                {'detalle': 'No puedes eliminar este pedido porque tiene productos asociados.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


# aqui va crud api de detalles
class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.select_related('pedido', 'producto').all().order_by('id')
    serializer_class = DetallePedidoSerializer
    permission_classes = [IsAuthenticated]

    # aqui devolvemos stock al eliminar un detalle
    def destroy(self, request, *args, **kwargs):
        detalle = self.get_object()
        producto = detalle.producto
        producto.stock += detalle.cantidad
        producto.save()
        return super().destroy(request, *args, **kwargs)


# aqui hacemos login api y devolvemos jwt
class ApiLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ApiLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = create_jwt_token(user)

        response = Response(
            {
                'mensaje': 'Login correcto.',
                'token': token,
                'usuario': {'id': user.id, 'username': user.username, 'email': user.email},
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            'jwt_token',
            token,
            httponly=True,
            samesite='Lax',
            max_age=30,
        )
        return response


# aqui hacemos logout api y limpiamos cookie
class ApiLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        response = Response({'mensaje': 'Logout correcto.'}, status=status.HTTP_200_OK)
        response.delete_cookie('jwt_token')
        return response


# aqui registramos usuario por api
class ApiRegistroView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ApiRegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'mensaje': 'Usuario registrado correctamente.',
                'usuario': {'id': user.id, 'username': user.username, 'email': user.email},
            },
            status=status.HTTP_201_CREATED,
        )
