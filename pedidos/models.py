from django.db import models


# aqui guardamos los datos basicos del cliente
class Cliente(models.Model):
    nombre    = models.CharField(max_length=100)
    correo    = models.EmailField()
    direccion = models.CharField(max_length=200)
    telefono  = models.CharField(max_length=20)

    # aqui mostramos el nombre cuando se imprime el cliente
    def __str__(self):
        return self.nombre


# aqui guardamos los productos que vendemos
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    stock  = models.IntegerField()

    # aqui mostramos el nombre cuando se imprime el producto
    def __str__(self):
        return self.nombre


# aqui guardamos la cabecera de cada pedido
class Pedido(models.Model):
    # aqui van los estados permitidos del pedido
    ESTADOS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviado',   'Enviado'),
        ('entregado', 'Entregado'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha   = models.DateField()
    estado  = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='pendiente')

    # aqui mostramos un resumen del pedido
    def __str__(self):
        return f"Pedido {self.id} - {self.cliente}"


# aqui guardamos cada linea de producto dentro de un pedido
class DetallePedido(models.Model):
    pedido   = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, blank=True)

    # aqui calculamos subtotal antes de guardar
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.producto.precio
        super().save(*args, **kwargs)

    # aqui mostramos producto y cantidad rapido
    def __str__(self):
        return f"{self.producto} x {self.cantidad}"
