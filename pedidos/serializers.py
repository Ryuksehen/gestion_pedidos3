from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from .models import Cliente, Producto, Pedido, DetallePedido


# aqui serializamos clientes para la api
class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'correo', 'direccion', 'telefono']


# aqui serializamos productos para la api
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'precio', 'stock']


# aqui serializamos pedidos para la api
class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['id', 'cliente', 'fecha', 'estado']


# aqui serializamos detalle de pedidos para la api
class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        fields = ['id', 'pedido', 'producto', 'cantidad', 'subtotal']
        read_only_fields = ['subtotal']

    # aqui validamos stock antes de crear
    def validate(self, attrs):
        producto = attrs.get('producto')
        cantidad = attrs.get('cantidad')
        if producto and cantidad and cantidad > producto.stock:
            raise serializers.ValidationError(
                {'cantidad': f'Solo hay {producto.stock} unidades disponibles.'}
            )
        return attrs

    # aqui descontamos stock al crear el detalle
    def create(self, validated_data):
        producto = validated_data['producto']
        cantidad = validated_data['cantidad']
        producto.stock -= cantidad
        producto.save()
        return super().create(validated_data)

    # aqui ajustamos stock al editar cantidad/producto
    def update(self, instance, validated_data):
        producto_original = instance.producto
        cantidad_original = instance.cantidad

        producto_nuevo = validated_data.get('producto', instance.producto)
        cantidad_nueva = validated_data.get('cantidad', instance.cantidad)

        # aqui devolvemos stock de lo anterior
        producto_original.stock += cantidad_original
        producto_original.save()

        # aqui validamos stock del nuevo estado
        if cantidad_nueva > producto_nuevo.stock:
            producto_original.stock -= cantidad_original
            producto_original.save()
            raise serializers.ValidationError(
                {'cantidad': f'Solo hay {producto_nuevo.stock} unidades disponibles.'}
            )

        producto_nuevo.stock -= cantidad_nueva
        producto_nuevo.save()

        return super().update(instance, validated_data)


# aqui serializamos login para api jwt
class ApiLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    # aqui validamos credenciales
    def validate(self, attrs):
        user = authenticate(username=attrs.get('username'), password=attrs.get('password'))
        if not user:
            raise serializers.ValidationError('Credenciales invalidas.')
        attrs['user'] = user
        return attrs


# aqui serializamos registro para api jwt
class ApiRegistroSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)

    # aqui creamos usuario nuevo
    def create(self, validated_data):
        UserModel = get_user_model()
        return UserModel.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
