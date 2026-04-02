from django import forms
# Importamos los modelos para enlazar cada formulario con su tabla en la base de datos
from .models import Pedido, Cliente, Producto, DetallePedido

# ─────────────────────────────────────────────────────────
# FORMULARIO: Pedido
# Permite crear y editar pedidos seleccionando el cliente,
# la fecha y el estado inicial.
# ─────────────────────────────────────────────────────────
class PedidoForm(forms.ModelForm):
    class Meta:
        model  = Pedido
        fields = ['cliente', 'fecha', 'estado']
        widgets = {
            # Select desplegable con estilo Bootstrap para elegir el cliente
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            # Input de tipo date para mostrar el selector de calendario nativo del navegador
            'fecha':   forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            # Select con las opciones definidas en ESTADOS_CHOICES del modelo
            'estado':  forms.Select(attrs={'class': 'form-control'}),
        }


# ─────────────────────────────────────────────────────────
# FORMULARIO: Cliente
# Gestiona el alta y edición de clientes.
# Incluye validaciones personalizadas para nombre y teléfono.
# ─────────────────────────────────────────────────────────
class ClienteForm(forms.ModelForm):
    class Meta:
        model  = Cliente
        fields = '__all__'  # Incluye todos los campos del modelo Cliente
        widgets = {
            'nombre':    forms.TextInput(attrs={'class': 'form-control'}),
            'correo':    forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono':  forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_nombre(self):
        # Validación personalizada: el nombre debe comenzar con una letra
        # strip() elimina espacios en blanco al inicio y al final
        nombre = self.cleaned_data.get('nombre', '').strip()
        if nombre and not nombre[0].isalpha():
            raise forms.ValidationError('El nombre debe comenzar con una letra.')
        return nombre

    def clean_telefono(self):
        # Validación personalizada: el teléfono solo debe contener dígitos
        telefono = self.cleaned_data.get('telefono', '').strip()
        if telefono and not telefono.isdigit():
            raise forms.ValidationError('El teléfono solo debe contener números.')
        return telefono


# ─────────────────────────────────────────────────────────
# FORMULARIO: Producto
# Gestiona el alta y edición de productos del catálogo.
# Incluye validaciones para nombre, precio y stock.
# ─────────────────────────────────────────────────────────
class ProductoForm(forms.ModelForm):
    class Meta:
        model  = Producto
        fields = '__all__'  # Incluye todos los campos del modelo Producto
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            # min='0' evita que el navegador acepte valores negativos antes de enviar
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'stock':  forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def clean_nombre(self):
        # Validación: el nombre del producto debe comenzar con una letra
        nombre = self.cleaned_data.get('nombre', '').strip()
        if nombre and not nombre[0].isalpha():
            raise forms.ValidationError('El nombre debe comenzar con una letra.')
        return nombre

    def clean_precio(self):
        # Validación en el servidor: el precio no puede ser un valor negativo
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio < 0:
            raise forms.ValidationError('El precio no puede ser negativo.')
        return precio

    def clean_stock(self):
        # Validación en el servidor: el stock no puede ser un valor negativo
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError('El stock no puede ser negativo.')
        return stock


# ─────────────────────────────────────────────────────────
# FORMULARIO: DetallePedido
# Permite agregar o editar una línea de detalle dentro de un pedido.
# Solo expone producto y cantidad; el subtotal se calcula en el modelo.
# ─────────────────────────────────────────────────────────
class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model  = DetallePedido
        fields = ['producto', 'cantidad']  # El campo 'subtotal' queda fuera del formulario
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            # min='1' garantiza que nunca se ingrese una cantidad de cero o negativa
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is not None and cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a 0.')
        return cantidad