from django.db import models

# ─────────────────────────────────────────────────────────
# MODELO: Cliente
# Almacena la información de contacto de cada cliente
# que puede realizar pedidos dentro del sistema.
# ─────────────────────────────────────────────────────────
class Cliente(models.Model):
    nombre    = models.CharField(max_length=100)   # Nombre completo del cliente
    correo    = models.EmailField()                # Correo electrónico (Django valida el formato)
    direccion = models.CharField(max_length=200)   # Dirección de entrega o contacto
    telefono  = models.CharField(max_length=20)    # Número de teléfono (cadena para permitir formatos varios)

    def __str__(self):
        # Representación legible usada en el admin y en los selects de formularios
        return self.nombre

# ─────────────────────────────────────────────────────────
# MODELO: Producto
# Representa los artículos disponibles en el catálogo.
# Controla el precio unitario y las unidades en stock.
# ─────────────────────────────────────────────────────────
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    # DecimalField con 12 dígitos en total y 2 decimales:
    # adecuado para valores monetarios y evita errores de punto flotante
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    stock  = models.IntegerField()  # Unidades disponibles en inventario

    def __str__(self):
        return self.nombre

# ─────────────────────────────────────────────────────────
# MODELO: Pedido
# Representa una orden de compra realizada por un cliente.
# Puede pasar por tres estados distintos en su ciclo de vida.
# ─────────────────────────────────────────────────────────
class Pedido(models.Model):
    # Opciones de estado que puede tomar un pedido
    ESTADOS_CHOICES = [
        ('pendiente', 'Pendiente'),   # Recién creado, aún no despachado
        ('enviado',   'Enviado'),     # En tránsito hacia el cliente
        ('entregado', 'Entregado'),   # Confirmado como recibido por el cliente
    ]

    # ForeignKey: un cliente puede tener muchos pedidos
    # CASCADE: si se elimina el cliente, se eliminan todos sus pedidos
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha   = models.DateField()  # Fecha en que se registra el pedido
    # choices restringe los valores válidos; default asigna 'pendiente' al crear
    estado  = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='pendiente')

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente}"

# ─────────────────────────────────────────────────────────
# MODELO: DetallePedido
# Representa una línea individual dentro de un pedido:
# qué producto se incluyó, en qué cantidad y cuánto suma.
# El subtotal se calcula automáticamente al guardar.
# ─────────────────────────────────────────────────────────
class DetallePedido(models.Model):
    # CASCADE: si se elimina el pedido, se eliminan todos sus detalles
    pedido   = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    # CASCADE: si se elimina el producto, se eliminan sus apariciones en detalles
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()  # Unidades del producto en este detalle
    # blank=True: el campo puede estar vacío en formularios; se rellena en save()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        # Calcula el subtotal automáticamente antes de persistir el registro:
        # subtotal = cantidad de unidades × precio unitario del producto
        self.subtotal = self.cantidad * self.producto.precio
        super().save(*args, **kwargs)  # Llama al save() original de Django

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"