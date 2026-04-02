# ─────────────────────────────────────────────────────────
# views/productos.py
# CRUD completo para el modelo Producto.
# ─────────────────────────────────────────────────────────
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView

from pedidos.models import Producto
from pedidos.forms import ProductoForm


# ─────────────────────────────────────────────────────────
# LISTAR PRODUCTOS
# ListView genera automáticamente la páginación y la consulta a la base de datos.
# ─────────────────────────────────────────────────────────
class ProductoListView(LoginRequiredMixin, ListView):
    model               = Producto
    template_name       = 'productos/listar.html'
    context_object_name = 'productos'  # Nombre de la variable disponible en el template
    paginate_by         = 10           # Máximo de registros por página
    ordering            = ['id']       # Orden ascendente por ID


# ─────────────────────────────────────────────────────────
# CREAR PRODUCTO
# GET  → muestra el formulario vacío
# POST → valida con ProductoForm (incluye validaciones de precio y stock) y guarda
# ─────────────────────────────────────────────────────────
@login_required
def crear_producto(request):
    if request.method == 'POST':
        # Inicializa el formulario con los datos enviados por el usuario
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()  # Persiste el nuevo producto en la base de datos
            messages.success(request, 'Producto creado correctamente')
            return redirect('listar_productos')
    else:
        # Para GET, muestra el formulario en blanco
        form = ProductoForm()
    return render(request, 'productos/crear.html', {'form': form})


# ─────────────────────────────────────────────────────────
# EDITAR PRODUCTO
# GET  → carga el formulario con los datos actuales del producto
# POST → valida y actualiza el registro
# ─────────────────────────────────────────────────────────
@login_required
def editar_producto(request, pk):
    # Buscar el producto o retornar 404 si no existe
    producto = get_object_or_404(Producto, pk=pk)
    # instance=producto vincula el formulario con el objeto existente
    form = ProductoForm(request.POST or None, instance=producto)
    if form.is_valid():
        form.save()  # Actualiza el registro en la base de datos
        messages.success(request, 'Producto actualizado correctamente')
        return redirect('listar_productos')
    return render(request, 'productos/editar.html', {'form': form})


# ─────────────────────────────────────────────────────────
# ELIMINAR PRODUCTO
# No se permite eliminar si el producto ya aparece en algún detalle de pedido,
# para preservar el historial de ventas como registro histórico.
# ─────────────────────────────────────────────────────────
@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    # detallepedido_set accede a los detalles relacionados con este producto
    if producto.detallepedido_set.exists():
        messages.error(request, 'No puedes eliminar un producto que ya forma parte de un pedido registrado')
        return redirect('listar_productos')
    producto.delete()  # Eliminar el producto de la base de datos
    messages.success(request, 'Producto eliminado correctamente del sistema')
    return redirect('listar_productos')
