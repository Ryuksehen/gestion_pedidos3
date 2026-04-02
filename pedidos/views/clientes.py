# ─────────────────────────────────────────────────────────
# views/clientes.py
# CRUD completo para el modelo Cliente.
# ─────────────────────────────────────────────────────────
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView

from pedidos.models import Cliente
from pedidos.forms import ClienteForm


# ─────────────────────────────────────────────────────────
# LISTAR CLIENTES
# ListView genera automáticamente la consulta, el contexto y la paginación.
# LoginRequiredMixin redirige a /login/ si el usuario no está autenticado.
# ─────────────────────────────────────────────────────────
class ClienteListView(LoginRequiredMixin, ListView):
    model               = Cliente
    template_name       = 'clientes/listar.html'
    context_object_name = 'clientes'   # Nombre de la variable en el template
    paginate_by         = 10           # Máximo de registros por página
    ordering            = ['id']       # Orden ascendente por ID


# ─────────────────────────────────────────────────────────
# CREAR CLIENTE
# GET  → muestra el formulario vacío
# POST → valida con ClienteForm (incluye clean_nombre y clean_telefono) y guarda
# ─────────────────────────────────────────────────────────
@login_required
def crear_cliente(request):
    if request.method == 'POST':
        # Inicializa el formulario con los datos enviados por el usuario
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()  # Persiste el nuevo cliente en la base de datos
            messages.success(request, 'Cliente creado correctamente')
            return redirect('listar_clientes')
    else:
        # Para GET, muestra el formulario en blanco
        form = ClienteForm()
    return render(request, 'clientes/crear.html', {'form': form})


# ─────────────────────────────────────────────────────────
# EDITAR CLIENTE
# GET  → carga el formulario con los datos actuales del cliente
# POST → valida y actualiza el registro
# ─────────────────────────────────────────────────────────
@login_required
def editar_cliente(request, pk):
    # Buscar el cliente o retornar 404 si no existe
    cliente = get_object_or_404(Cliente, pk=pk)
    # instance=cliente vincula el formulario con el objeto existente para edición
    form = ClienteForm(request.POST or None, instance=cliente)
    if form.is_valid():
        form.save()  # Actualiza el registro en la base de datos
        messages.success(request, 'Cliente actualizado correctamente')
        return redirect('listar_clientes')
    return render(request, 'clientes/editar.html', {'form': form})


# ─────────────────────────────────────────────────────────
# ELIMINAR CLIENTE
# Solo se permite eliminar si el cliente no tiene pedidos asociados,
# para preservar la integridad referencial de los datos.
# ─────────────────────────────────────────────────────────
@login_required
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    # Verificar si el cliente tiene pedidos antes de eliminarlo
    if cliente.pedido_set.exists():
        messages.error(request, 'No puedes eliminar este cliente porque tiene pedidos asociados')
        return redirect('listar_clientes')
    cliente.delete()  # Eliminar el cliente de la base de datos
    messages.success(request, 'Cliente eliminado correctamente')
    return redirect('listar_clientes')
