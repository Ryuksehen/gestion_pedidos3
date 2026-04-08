from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView

from pedidos.models import Pedido
from pedidos.forms import PedidoForm


# aqui listamos pedidos con paginacion
class PedidoListView(LoginRequiredMixin, ListView):
    model              = Pedido
    template_name      = 'pedidos/listar.html'
    context_object_name = 'pedidos'
    paginate_by        = 10
    ordering           = ['id']


# aqui creamos pedidos nuevos
@login_required
def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pedido creado correctamente')
            return redirect('listar')
    else:
        form = PedidoForm()
    return render(request, 'pedidos/crear.html', {'form': form})


# aqui editamos pedidos existentes
@login_required
def editar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    form = PedidoForm(request.POST or None, instance=pedido)
    if form.is_valid():
        form.save()
        messages.success(request, 'Pedido actualizado correctamente')
        return redirect('listar')
    return render(request, 'pedidos/editar.html', {'form': form})


# aqui borramos pedido si no tiene detalles
@login_required
def eliminar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if pedido.detallepedido_set.exists():
        messages.error(request, 'No puedes eliminar este pedido porque tiene productos asociados')
        return redirect('listar')
    pedido.delete()
    messages.success(request, 'Pedido eliminado correctamente')
    return redirect('listar')


# aqui mostramos detalle completo del pedido
@login_required
def detalle_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    return render(request, 'pedidos/detalle.html', {'pedido': pedido})

