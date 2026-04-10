from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView
from datetime import date

from pedidos.models import Pedido, Cliente, Producto, DetallePedido
from pedidos.forms import PedidoForm, DetallePedidoForm


# aqui listamos pedidos con paginacion
class PedidoListView(LoginRequiredMixin, ListView):
    model              = Pedido
    template_name      = 'pedidos/listar.html'
    context_object_name = 'pedidos'
    paginate_by        = 10
    ordering           = ['id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pedidos = context['pedidos']
        context['form_crear_pedido'] = PedidoForm()
        context['formularios_editar_pedido'] = [(pedido, PedidoForm(instance=pedido)) for pedido in pedidos]
        context['clientes_disponibles'] = Cliente.objects.all().order_by('nombre')
        context['productos_disponibles'] = Producto.objects.filter(stock__gt=0).order_by('nombre')
        return context


# aqui creamos pedido y primer producto en un solo paso
@login_required
def crear_pedido_con_producto(request):
    if request.method != 'POST':
        return redirect('listar')

    cliente_id = request.POST.get('cliente_id')
    producto_id = request.POST.get('producto_id')
    cantidad_raw = request.POST.get('cantidad')

    if not cliente_id or not producto_id or not cantidad_raw:
        messages.error(request, 'Debes seleccionar cliente, producto y cantidad.')
        return redirect('listar')

    try:
        cantidad = int(cantidad_raw)
    except (TypeError, ValueError):
        messages.error(request, 'La cantidad debe ser un número válido.')
        return redirect('listar')

    if cantidad <= 0:
        messages.error(request, 'La cantidad debe ser mayor a 0.')
        return redirect('listar')

    cliente = get_object_or_404(Cliente, pk=cliente_id)
    producto = get_object_or_404(Producto, pk=producto_id)

    if cantidad > producto.stock:
        messages.error(request, f'No hay stock suficiente. Solo quedan {producto.stock} unidades.')
        return redirect('listar')

    pedido = Pedido.objects.create(
        cliente=cliente,
        fecha=date.today(),
        estado='pendiente',
    )

    DetallePedido.objects.create(
        pedido=pedido,
        producto=producto,
        cantidad=cantidad,
    )

    producto.stock -= cantidad
    producto.save()

    messages.success(request, f'Pedido #{pedido.id} creado con producto agregado.')
    return redirect('listar')


# aqui creamos pedidos nuevos
@login_required
def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pedido creado correctamente')
            return redirect('listar')
        messages.error(request, 'No se pudo crear el pedido. Revisa los datos del formulario.')
        return redirect('listar')
    else:
        return redirect('listar')


# aqui editamos pedidos existentes
@login_required
def editar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    form = PedidoForm(request.POST or None, instance=pedido)
    if form.is_valid():
        form.save()
        messages.success(request, 'Pedido actualizado correctamente')
        return redirect('listar')
    if request.method == 'POST':
        messages.error(request, 'No se pudo actualizar el pedido. Revisa los datos del formulario.')
    return redirect('listar')


# aqui borramos pedido si no tiene detalles
@login_required
@require_POST
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
    form_agregar_detalle = DetallePedidoForm()
    formularios_editar_detalle = [(detalle, DetallePedidoForm(instance=detalle)) for detalle in pedido.detallepedido_set.all()]
    return render(
        request,
        'pedidos/detalle.html',
        {
            'pedido': pedido,
            'form_agregar_detalle': form_agregar_detalle,
            'formularios_editar_detalle': formularios_editar_detalle,
        },
    )

