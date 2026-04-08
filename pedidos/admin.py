from django.contrib import admin
from .models import Pedido
from .models import Cliente
from .models import Producto

admin.site.register(Pedido)

admin.site.register(Cliente)

admin.site.register(Producto)
