from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
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
        cantidad = attrs.get('cantidad')

        # para PATCH, usamos la cantidad actual si no viene en attrs
        if cantidad is None and self.instance is not None:
            cantidad = self.instance.cantidad

        if cantidad is None:
            raise serializers.ValidationError({'cantidad': 'La cantidad es obligatoria.'})

        if cantidad <= 0:
            raise serializers.ValidationError({'cantidad': 'La cantidad debe ser mayor a 0.'})

        producto = attrs.get('producto')
        if self.instance is None and producto and cantidad > producto.stock:
            raise serializers.ValidationError(
                {'cantidad': f'Solo hay {producto.stock} unidades disponibles.'}
            )
        return attrs

    # aqui descontamos stock al crear el detalle
    def create(self, validated_data):
        cantidad = validated_data['cantidad']
        producto_id = validated_data['producto'].id

        with transaction.atomic():
            producto = Producto.objects.select_for_update().get(id=producto_id)

            if cantidad > producto.stock:
                raise serializers.ValidationError(
                    {'cantidad': f'Solo hay {producto.stock} unidades disponibles.'}
                )

            producto.stock -= cantidad
            producto.save(update_fields=['stock'])

            validated_data['producto'] = producto
            return super().create(validated_data)

    # aqui ajustamos stock al editar cantidad/producto
    def update(self, instance, validated_data):
        cantidad_nueva = validated_data.get('cantidad', instance.cantidad)

        with transaction.atomic():
            detalle_actual = DetallePedido.objects.select_for_update().get(id=instance.id)

            producto_original_id = detalle_actual.producto_id
            cantidad_original = detalle_actual.cantidad

            producto_nuevo_obj = validated_data.get('producto', detalle_actual.producto)
            producto_nuevo_id = producto_nuevo_obj.id

            ids_productos = sorted({producto_original_id, producto_nuevo_id})
            productos = {
                p.id: p for p in Producto.objects.select_for_update().filter(id__in=ids_productos)
            }

            producto_original = productos[producto_original_id]
            producto_nuevo = productos[producto_nuevo_id]

            # devolvemos primero el stock anterior
            producto_original.stock += cantidad_original

            # y luego validamos contra stock disponible actualizado
            if cantidad_nueva > producto_nuevo.stock:
                raise serializers.ValidationError(
                    {'cantidad': f'Solo hay {producto_nuevo.stock} unidades disponibles.'}
                )

            producto_nuevo.stock -= cantidad_nueva

            producto_original.save(update_fields=['stock'])
            if producto_nuevo.id != producto_original.id:
                producto_nuevo.save(update_fields=['stock'])

            validated_data['producto'] = producto_nuevo
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
