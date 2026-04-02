# ─────────────────────────────────────────────────────────
# views/pedidos.py
# CRUD completo para el modelo Pedido.
# ─────────────────────────────────────────────────────────
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView

from pedidos.models import Pedido
from pedidos.forms import PedidoForm


# ─────────────────────────────────────────────────────────
# LISTAR PEDIDOS
# Usa ListView de Django para generar automáticamente la paginación.
# LoginRequiredMixin redirige a /login/ si el usuario no está autenticado.
# ─────────────────────────────────────────────────────────
class PedidoListView(LoginRequiredMixin, ListView):
    model              = Pedido
    template_name      = 'pedidos/listar.html'
    context_object_name = 'pedidos'   # Nombre de la variable en el template
    paginate_by        = 10           # Máximo de registros por página
    ordering           = ['id']       # Ordena los pedidos ascendentemente por ID


# ─────────────────────────────────────────────────────────
# CREAR PEDIDO
# GET  → muestra el formulario vacío
# POST → valida y guarda el nuevo pedido
# ─────────────────────────────────────────────────────────
@login_required
def crear_pedido(request):
    if request.method == 'POST':
        # Inicializa el formulario con los datos enviados por el usuario
        form = PedidoForm(request.POST)
        if form.is_valid():
            form.save()  # Persiste el pedido en la base de datos
            messages.success(request, 'Pedido creado correctamente')
            return redirect('listar')  # Redirige al listado tras el éxito
    else:
        # Para GET, se muestra el formulario en blanco
        form = PedidoForm()
    return render(request, 'pedidos/crear.html', {'form': form})


# ─────────────────────────────────────────────────────────
# EDITAR PEDIDO
# GET  → muestra el formulario pre-cargado con los datos del pedido
# POST → valida y actualiza el pedido existente
# get_object_or_404 devuelve 404 si el pedido no existe
# ─────────────────────────────────────────────────────────
@login_required
def editar_pedido(request, pk):
    # Buscar el pedido por su clave primaria; retornar 404 si no existe
    pedido = get_object_or_404(Pedido, pk=pk)
    # instance=pedido vincula el formulario con el objeto existente
    form = PedidoForm(request.POST or None, instance=pedido)
    if form.is_valid():
        form.save()  # Actualiza el registro en la base de datos
        messages.success(request, 'Pedido actualizado correctamente')
        return redirect('listar')
    return render(request, 'pedidos/editar.html', {'form': form})


# ─────────────────────────────────────────────────────────
# ELIMINAR PEDIDO
# Solo se permite eliminar si el pedido no tiene detalles asociados,
# para preservar la integridad referencial de los datos.
# ─────────────────────────────────────────────────────────
@login_required
def eliminar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    # Verificar si el pedido tiene líneas de detalle antes de eliminarlo
    if pedido.detallepedido_set.exists():
        messages.error(request, 'No puedes eliminar este pedido porque tiene productos asociados')
        return redirect('listar')
    pedido.delete()  # Eliminar el pedido de la base de datos
    messages.success(request, 'Pedido eliminado correctamente')
    return redirect('listar')


# ─────────────────────────────────────────────────────────
# DETALLE DE PEDIDO
# Muestra la vista completa de un pedido individual
# incluyendo todos sus productos (líneas de detalle).
# ─────────────────────────────────────────────────────────
@login_required
def detalle_pedido(request, pk):
    # Obtener el pedido o retornar 404 si no existe
    pedido = get_object_or_404(Pedido, pk=pk)
    # El template accede a los detalles mediante la relación inversa detallepedido_set
    return render(request, 'pedidos/detalle.html', {'pedido': pedido})
