from datetime import date

from django import forms

from .models import Pedido, Cliente, Producto, DetallePedido


# aqui va el formulario de pedidos
class PedidoForm(forms.ModelForm):
    # aqui decimos que campos salen en el formulario de pedido
    class Meta:
        model  = Pedido
        fields = ['cliente', 'fecha', 'estado']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'fecha':   forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estado':  forms.Select(attrs={'class': 'form-control'}),
        }

    # aqui validamos que la fecha tenga sentido
    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if not fecha:
            raise forms.ValidationError('La fecha es obligatoria.')
        if fecha > date.today():
            raise forms.ValidationError('La fecha no puede ser futura.')
        return fecha

    # aqui validamos que el estado exista en la lista
    def clean_estado(self):
        estado = self.cleaned_data.get('estado', '').strip()
        estados_validos = [item[0] for item in Pedido.ESTADOS_CHOICES]
        if estado not in estados_validos:
            raise forms.ValidationError('Seleccione un estado valido.')
        return estado


# aqui va el formulario de clientes
class ClienteForm(forms.ModelForm):
    # aqui elegimos todos los campos del cliente
    class Meta:
        model  = Cliente
        fields = '__all__'
        widgets = {
            'nombre':    forms.TextInput(attrs={'class': 'form-control'}),
            'correo':    forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono':  forms.TextInput(attrs={'class': 'form-control'}),
        }

    # aqui revisamos que el nombre no venga raro
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        if not nombre[0].isalpha():
            raise forms.ValidationError('El nombre debe iniciar con una letra.')
        return nombre

    # aqui validamos el correo de forma basica
    def clean_correo(self):
        correo = self.cleaned_data.get('correo', '').strip().lower()
        if '@' not in correo or '.' not in correo.split('@')[-1]:
            raise forms.ValidationError('Ingrese un correo valido.')
        return correo

    # aqui validamos telefono solo con numeros
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if not telefono:
            raise forms.ValidationError('El telefono es obligatorio.')
        if not telefono.isdigit():
            raise forms.ValidationError('El teléfono solo debe contener números.')
        if len(telefono) < 7 or len(telefono) > 15:
            raise forms.ValidationError('El telefono debe tener entre 7 y 15 digitos.')
        return telefono


# aqui va el formulario de productos
class ProductoForm(forms.ModelForm):
    # aqui definimos campos y estilo rapido para producto
    class Meta:
        model  = Producto
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'stock':  forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    # aqui validamos nombre de producto
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 2:
            raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
        if nombre.isdigit():
            raise forms.ValidationError('El nombre no puede ser solo numeros.')
        return nombre

    # aqui revisamos que el precio sea mayor a cero
    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is None:
            raise forms.ValidationError('El precio es obligatorio.')
        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0.')
        return precio

    # aqui validamos un stock razonable
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is None:
            raise forms.ValidationError('El stock es obligatorio.')
        if stock < 0:
            raise forms.ValidationError('El stock no puede ser negativo.')
        if stock > 100000:
            raise forms.ValidationError('El stock es demasiado alto.')
        return stock


# aqui va el formulario para agregar productos al pedido
class DetallePedidoForm(forms.ModelForm):
    # aqui dejamos solo producto y cantidad
    class Meta:
        model  = DetallePedido
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    # aqui obligamos a elegir un producto
    def clean_producto(self):
        producto = self.cleaned_data.get('producto')
        if not producto:
            raise forms.ValidationError('Debe seleccionar un producto.')
        return producto

    # aqui validamos que la cantidad sea correcta
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None:
            raise forms.ValidationError('La cantidad es obligatoria.')
        if cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor a 0.')
        if cantidad > 1000:
            raise forms.ValidationError('La cantidad maxima permitida es 1000.')
        return cantidad
