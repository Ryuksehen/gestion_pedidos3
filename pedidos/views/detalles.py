# ─────────────────────────────────────────────────────────
# views/detalles.py
# CRUD de DetallePedido (líneas de producto dentro de un pedido).
# Todas las operaciones actualizan el stock del producto automáticamente.
# ─────────────────────────────────────────────────────────
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView

from pedidos.models import Pedido, DetallePedido, Producto
from pedidos.forms import DetallePedidoForm


# ─────────────────────────────────────────────────────────
# LISTAR TODOS LOS DETALLES
# Muestra todos los detalles de pedido del sistema (no filtrado por pedido).
# ─────────────────────────────────────────────────────────
class DetallePedidoListView(LoginRequiredMixin, ListView):
    model               = DetallePedido
    template_name       = 'pedidos/listar_detalles.html'
    context_object_name = 'detalles'  # Nombre de la variable en el template
    paginate_by         = 10          # Máximo de registros por página
    ordering            = ['id']


# ─────────────────────────────────────────────────────────
# AGREGAR DETALLE A UN PEDIDO
# Agrega una nueva línea de producto a un pedido existente.
# Valida que haya suficiente stock antes de guardar.
# Descuenta del stock del producto al confirmar.
# ─────────────────────────────────────────────────────────
@login_required
def agregar_detalle(request, pedido_id):
    # Obtener el pedido al que se va a agregar el detalle
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        form = DetallePedidoForm(request.POST)
        if form.is_valid():
            # commit=False permite modificar el objeto antes de persistirlo
            detalle  = form.save(commit=False)
            detalle.pedido = pedido  # Asignar el pedido al detalle
            producto = detalle.producto
            cantidad = detalle.cantidad
            # Verificar disponibilidad: no se puede pedir más de lo que hay en stock
            if cantidad > producto.stock:
                messages.error(request, f'No puedes agregar {cantidad}. Solo quedan {producto.stock} unidades en stock.')
                return redirect('detalle', pk=pedido.id)
            # Descontar del inventario la cantidad solicitada
            producto.stock -= cantidad
            producto.save()
            detalle.save()  # Persiste el detalle (save() del modelo calcula el subtotal)
            messages.success(request, 'Producto agregado al pedido')
            return redirect('detalle', pk=pedido.id)
    else:
        form = DetallePedidoForm()
    return render(request, 'pedidos/agregar_detalle.html', {'form': form, 'pedido': pedido})


# ─────────────────────────────────────────────────────────
# EDITAR DETALLE
# Ajusta la cantidad de un producto en un pedido existente.
# Restaura primero la cantidad anterior al stock, luego aplica la nueva.
# ─────────────────────────────────────────────────────────
@login_required
def editar_detalle(request, pk):
    detalle            = get_object_or_404(DetallePedido, pk=pk)
    producto           = detalle.producto
    cantidad_anterior  = detalle.cantidad  # Guardamos la cantidad original para devolverla al stock
    form = DetallePedidoForm(request.POST or None, instance=detalle)
    if form.is_valid():
        detalle_editado = form.save(commit=False)
        nueva_cantidad  = detalle_editado.cantidad
        # Devolver la cantidad original al inventario antes de aplicar la nueva
        producto.stock += cantidad_anterior
        # Verificar si el stock disponible (restaurado) alcanza la nueva cantidad
        if nueva_cantidad > producto.stock:
            messages.error(request, f'Cantidad máxima disponible: {producto.stock}')
            return redirect('detalle', pk=detalle.pedido.id)
        # Aplicar el descuento con la nueva cantidad al inventario
        producto.stock -= nueva_cantidad
        producto.save()
        detalle_editado.save()  # Persiste el detalle actualizado
        messages.success(request, 'Producto actualizado correctamente')
        return redirect('detalle', pk=detalle.pedido.id)
    return render(request, 'pedidos/editar_detalle.html', {'form': form})


# ─────────────────────────────────────────────────────────
# ELIMINAR DETALLE
# Reintegra al inventario las unidades del producto antes de eliminar el detalle.
# ─────────────────────────────────────────────────────────
@login_required
def eliminar_detalle(request, pk):
    detalle              = get_object_or_404(DetallePedido, pk=pk)
    producto             = detalle.producto
    cantidad_a_devolver  = detalle.cantidad  # Unidades que se devolverán al stock
    pedido_id            = detalle.pedido.id  # ID del pedido para redirigir al final
    # Devolver las unidades al inventario del producto
    producto.stock += cantidad_a_devolver
    producto.save()
    detalle.delete()  # Eliminar el detalle de la base de datos
    messages.success(request, 'Producto eliminado correctamente')
    # Redirigir al detalle del pedido al que pertenecía el detalle eliminado
    return redirect('detalle', pk=pedido_id)
