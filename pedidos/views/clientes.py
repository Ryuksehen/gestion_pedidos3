from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView

from pedidos.models import Cliente
from pedidos.forms import ClienteForm


# aqui listamos clientes con paginacion
class ClienteListView(LoginRequiredMixin, ListView):
    model               = Cliente
    template_name       = 'clientes/listar.html'
    context_object_name = 'clientes'
    paginate_by         = 10
    ordering            = ['id']


# aqui creamos un cliente nuevo
@login_required
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado correctamente')
            return redirect('listar_clientes')
    else:
        form = ClienteForm()
    return render(request, 'clientes/crear.html', {'form': form})


# aqui editamos un cliente existente
@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)
    if form.is_valid():
        form.save()
        messages.success(request, 'Cliente actualizado correctamente')
        return redirect('listar_clientes')
    return render(request, 'clientes/editar.html', {'form': form})


# aqui borramos cliente si no tiene pedidos
@login_required
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if cliente.pedido_set.exists():
        messages.error(request, 'No puedes eliminar este cliente porque tiene pedidos asociados')
        return redirect('listar_clientes')
    cliente.delete()
    messages.success(request, 'Cliente eliminado correctamente')
    return redirect('listar_clientes')

