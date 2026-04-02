from django.contrib import admin

# Register your models here.
from .models import Pedido
# imortamos clientes
from .models import Cliente
# Importamos productos
from .models import Producto

admin.site.register(Pedido)

admin.site.register(Cliente)

admin.site.register(Producto)