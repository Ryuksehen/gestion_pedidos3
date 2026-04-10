from datetime import date

from django.test import TestCase

from pedidos.models import Cliente, Pedido, Producto
from pedidos.serializers import DetallePedidoSerializer


class DetallePedidoSerializerTests(TestCase):
	def setUp(self):
		self.cliente = Cliente.objects.create(
			nombre='Cliente Test',
			correo='cliente@test.com',
			direccion='Av Test 123',
			telefono='999999999',
		)
		self.producto = Producto.objects.create(
			nombre='Producto Test',
			precio='10.00',
			stock=10,
		)
		self.pedido = Pedido.objects.create(
			cliente=self.cliente,
			fecha=date.today(),
			estado='pendiente',
		)

	def test_rechaza_cantidad_negativa(self):
		serializer = DetallePedidoSerializer(
			data={
				'pedido': self.pedido.id,
				'producto': self.producto.id,
				'cantidad': -1,
			}
		)

		self.assertFalse(serializer.is_valid())
		self.assertIn('cantidad', serializer.errors)

	def test_rechaza_cantidad_cero(self):
		serializer = DetallePedidoSerializer(
			data={
				'pedido': self.pedido.id,
				'producto': self.producto.id,
				'cantidad': 0,
			}
		)

		self.assertFalse(serializer.is_valid())
		self.assertIn('cantidad', serializer.errors)

	def test_create_descuenta_stock(self):
		serializer = DetallePedidoSerializer(
			data={
				'pedido': self.pedido.id,
				'producto': self.producto.id,
				'cantidad': 3,
			}
		)

		self.assertTrue(serializer.is_valid(), serializer.errors)
		serializer.save()

		self.producto.refresh_from_db()
		self.assertEqual(self.producto.stock, 7)

	def test_update_ajusta_stock_mismo_producto(self):
		serializer_create = DetallePedidoSerializer(
			data={
				'pedido': self.pedido.id,
				'producto': self.producto.id,
				'cantidad': 2,
			}
		)
		self.assertTrue(serializer_create.is_valid(), serializer_create.errors)
		detalle = serializer_create.save()

		serializer_update = DetallePedidoSerializer(
			instance=detalle,
			data={
				'pedido': self.pedido.id,
				'producto': self.producto.id,
				'cantidad': 5,
			},
		)
		self.assertTrue(serializer_update.is_valid(), serializer_update.errors)
		serializer_update.save()

		self.producto.refresh_from_db()
		self.assertEqual(self.producto.stock, 5)

