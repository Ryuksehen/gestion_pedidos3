from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView

from pedidos.models import Producto
from pedidos.forms import ProductoForm


# aqui listamos productos con paginacion
class ProductoListView(LoginRequiredMixin, ListView):
    model               = Producto
    template_name       = 'productos/listar.html'
    context_object_name = 'productos'
    paginate_by         = 10
    ordering            = ['id']


# aqui creamos producto nuevo
@login_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado correctamente')
            return redirect('listar_productos')
    else:
        form = ProductoForm()
    return render(request, 'productos/crear.html', {'form': form})


# aqui editamos producto existente
@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, instance=producto)
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto actualizado correctamente')
        return redirect('listar_productos')
    return render(request, 'productos/editar.html', {'form': form})


# aqui eliminamos producto si no tiene detalles
@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if producto.detallepedido_set.exists():
        messages.error(request, 'No puedes eliminar un producto que ya forma parte de un pedido registrado')
        return redirect('listar_productos')
    producto.delete()
    messages.success(request, 'Producto eliminado correctamente del sistema')
    return redirect('listar_productos')

