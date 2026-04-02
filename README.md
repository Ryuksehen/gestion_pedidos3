# Sistema de Gestión de Pedidos

Aplicación web desarrollada con **Django 6** y **MySQL** para la gestión de pedidos, clientes, productos y detalles de pedido. Incluye autenticación con JWT, paginación, alertas con SweetAlert2, y exportación de reportes en PDF, Excel y JSON.

---

## Tabla de contenidos

1. [Instalación del entorno](#1-instalación-del-entorno)
2. [Creación del proyecto](#2-creación-del-proyecto)
3. [Modelos](#3-modelos)
4. [Migraciones](#4-migraciones)
5. [Vistas CRUD](#5-vistas-crud)
6. [Templates](#6-templates)
7. [Paginación](#7-paginación)
8. [SweetAlert2](#8-sweetalert2)
9. [Exportación PDF y Excel](#9-exportación-pdf-y-excel)
10. [Capturas paso a paso](#10-capturas-paso-a-paso)

---

## 1. Instalación del entorno

### Requisitos previos

| Herramienta | Versión recomendada |
|-------------|---------------------|
| Python      | 3.11+               |
| MySQL       | 8.0+                |
| pip         | última              |

### Paso 1 — Crear el entorno virtual

```bash
# Desde la carpeta raíz del proyecto
python -m venv env
```

### Paso 2 — Activar el entorno virtual

```bash
# Windows
env\Scripts\activate

> Una vez activado, el prompt del terminal mostrará `(env)` al inicio.

### Paso 3 — Instalar las dependencias

```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` contiene:

```
Django==6.0.3
mysqlclient==2.2.8
openpyxl==3.1.5
reportlab==4.4.10
Pillow==12.1.1
sqlparse==0.5.5
tzdata==2025.3
asgiref==3.11.1
```

### Paso 4 — Crear la base de datos en MySQL

```sql
CREATE DATABASE gestion_pedidos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Paso 5 — Configurar la conexión a la base de datos

Editar `proyecto_pedidos/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gestion_pedidos',
        'USER': 'root',
        'PASSWORD': '123456',   # <-- cambiar por tu contraseña
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

---

## 2. Creación del proyecto

### Estructura generada

```
gestion_pedidos3/
├── manage.py
├── requirements.txt
├── env/                          # Entorno virtual
├── proyecto_pedidos/             # Configuración global
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── pedidos/                      # Aplicación principal
    ├── models.py
    ├── forms.py
    ├── urls.py
    ├── admin.py
    ├── middleware.py
    ├── reportes.py
    ├── migrations/
    ├── views/
    │   ├── __init__.py
    │   ├── auth.py
    │   ├── clientes.py
    │   ├── detalles.py
    │   ├── pedidos.py
    │   └── productos.py
    └── templates/
        ├── base.html
        ├── clientes/
        ├── pedidos/
        └── productos/
```

### Comandos de creación (referencia)

```bash
# Crear el proyecto
django-admin startproject proyecto_pedidos

# Crear la aplicación
python manage.py startapp pedidos
```

### Registrar la aplicación

En `proyecto_pedidos/settings.py`, agregar `'pedidos'` en `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'pedidos',
]
```

### Configurar URLs principales

`proyecto_pedidos/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pedidos.urls')),
]
```

### Configuración de autenticación

```python
# settings.py
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
```

---

## 3. Modelos

Los modelos se definen en `pedidos/models.py`. El proyecto gestiona cuatro entidades relacionadas:

```
Cliente ──< Pedido ──< DetallePedido >── Producto
```

### Cliente

```python
class Cliente(models.Model):
    nombre    = models.CharField(max_length=100)
    correo    = models.EmailField()
    direccion = models.CharField(max_length=200)
    telefono  = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre
```

| Campo     | Tipo          | Descripción            |
|-----------|---------------|------------------------|
| nombre    | CharField     | Nombre del cliente     |
| correo    | EmailField    | Correo electrónico     |
| direccion | CharField     | Dirección física       |
| telefono  | CharField     | Número de teléfono     |

### Producto

```python
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    stock  = models.IntegerField()

    def __str__(self):
        return self.nombre
```

| Campo  | Tipo          | Descripción                |
|--------|---------------|----------------------------|
| nombre | CharField     | Nombre del producto        |
| precio | DecimalField  | Precio unitario (12,2)     |
| stock  | IntegerField  | Unidades disponibles       |

### Pedido

```python
class Pedido(models.Model):
    ESTADOS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviado',   'Enviado'),
        ('entregado', 'Entregado'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha   = models.DateField()
    estado  = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='pendiente')

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente}"
```

| Campo   | Tipo        | Descripción                              |
|---------|-------------|------------------------------------------|
| cliente | ForeignKey  | Relación con Cliente (CASCADE)           |
| fecha   | DateField   | Fecha del pedido                         |
| estado  | CharField   | pendiente / enviado / entregado          |

### DetallePedido

```python
class DetallePedido(models.Model):
    pedido   = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.producto.precio
        super().save(*args, **kwargs)
```

> El `subtotal` se calcula automáticamente al guardar: `cantidad × precio`.

---

## 4. Migraciones

### Crear migraciones

```bash
python manage.py makemigrations
```

Esto genera los archivos en `pedidos/migrations/`:

```
migrations/
├── 0001_initial.py               # Creación de las 4 tablas
└── 0002_alter_pedido_estado.py   # Ajuste del campo estado
```

### Aplicar migraciones

```bash
python manage.py migrate
```

Salida esperada:

```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, pedidos, sessions
Running migrations:
  Applying pedidos.0001_initial... OK
  Applying pedidos.0002_alter_pedido_estado... OK
```

### Crear superusuario

```bash
python manage.py createsuperuser
```

### Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

Acceder en el navegador: `http://127.0.0.1:8000/`

---

## 5. Vistas CRUD

Las vistas están organizadas en el paquete `pedidos/views/` con un archivo por módulo.

### Estructura de views

```
views/
├── __init__.py      # Re-exporta todas las vistas
├── auth.py          # Login, Logout, Registro + JWT
├── clientes.py      # CRUD de clientes
├── pedidos.py       # CRUD de pedidos
├── productos.py     # CRUD de productos
└── detalles.py      # CRUD de detalles de pedido
```

### Patrón CRUD aplicado

Todas las entidades siguen el mismo patrón de cuatro operaciones:

#### Listar (ListView con paginación)

```python
class PedidoListView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'pedidos/listar.html'
    context_object_name = 'pedidos'
    paginate_by = 10
    ordering = ['id']
```

#### Crear

```python
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
```

#### Editar

```python
@login_required
def editar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    form = PedidoForm(request.POST or None, instance=pedido)
    if form.is_valid():
        form.save()
        messages.success(request, 'Pedido actualizado correctamente')
        return redirect('listar')
    return render(request, 'pedidos/editar.html', {'form': form})
```

#### Eliminar (con validación de integridad)

```python
@login_required
def eliminar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if pedido.detallepedido_set.exists():
        messages.error(request, 'No puedes eliminar este pedido porque tiene productos asociados')
        return redirect('listar')
    pedido.delete()
    messages.success(request, 'Pedido eliminado correctamente')
    return redirect('listar')
```

### Formularios (forms.py)

Los formularios usan `ModelForm` con validaciones personalizadas:

```python
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'nombre':    forms.TextInput(attrs={'class': 'form-control'}),
            'correo':    forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono':  forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if nombre and not nombre[0].isalpha():
            raise forms.ValidationError('El nombre debe comenzar con una letra.')
        return nombre

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if telefono and not telefono.isdigit():
            raise forms.ValidationError('El teléfono solo debe contener números.')
        return telefono
```

### URLs registradas

```python
# pedidos/urls.py

# Pedidos
path('',                              views.home_view,               name='home'),
path('listar/',                       views.PedidoListView.as_view(), name='listar'),
path('crear/',                        views.crear_pedido,             name='crear'),
path('editar/<int:pk>/',              views.editar_pedido,            name='editar'),
path('eliminar/<int:pk>/',            views.eliminar_pedido,          name='eliminar'),
path('detalle/<int:pk>/',             views.detalle_pedido,           name='detalle'),

# Clientes
path('clientes/',                     views.ClienteListView.as_view(), name='listar_clientes'),
path('clientes/crear/',               views.crear_cliente,             name='crear_cliente'),
path('clientes/editar/<int:pk>/',     views.editar_cliente,            name='editar_cliente'),
path('clientes/eliminar/<int:pk>/',   views.eliminar_cliente,          name='eliminar_cliente'),

# Productos
path('productos/',                    views.ProductoListView.as_view(), name='listar_productos'),
path('productos/crear/',              views.crear_producto,             name='crear_producto'),
path('productos/editar/<int:pk>/',    views.editar_producto,            name='editar_producto'),
path('productos/eliminar/<int:pk>/',  views.eliminar_producto,          name='eliminar_producto'),

# Detalles
path('detalles/',                          views.DetallePedidoListView.as_view(), name='listar_detalles'),
path('pedido/<int:pedido_id>/agregar/',    views.agregar_detalle,                 name='agregar_detalle'),
path('detalle/editar/<int:pk>/',           views.editar_detalle,                  name='editar_detalle'),
path('detalle/eliminar/<int:pk>/',         views.eliminar_detalle,                name='eliminar_detalle'),
```

### Autenticación con JWT

El proyecto implementa JWT propio (sin dependencias externas), almacenado como cookie `httponly`:

```python
# views/auth.py
def create_jwt_token(user, expires_in=3600):
    header  = {'alg': 'HS256', 'typ': 'JWT'}
    payload = {
        'user_id':  user.id,
        'username': user.username,
        'exp':      int(time.time()) + expires_in,
    }
    # firma con HMAC-SHA256 usando SECRET_KEY
    ...
```

El `JWTAuthenticationMiddleware` en `pedidos/middleware.py` lee el token desde la cookie o el header `Authorization: Bearer <token>` y asocia el usuario a la request.

---

## 6. Templates

Los templates usan **herencia** con `base.html` como plantilla padre.

### base.html

Incluye desde CDN:
- **Bootstrap 5.3** (CSS + JS)
- **Bootstrap Icons 1.11**
- **SweetAlert2 v11**

```html
{% block content %}
{% endblock %}
```

### Organización de templates

```
templates/
├── base.html                    # Layout principal con sidebar
├── pedidos/
│   ├── listar.html              # Tabla con paginación y exportación
│   ├── crear.html               # Formulario de alta
│   ├── editar.html              # Formulario de edición
│   ├── detalle.html             # Vista detalle de un pedido
│   ├── listar_detalles.html     # Tabla de todos los detalles
│   ├── agregar_detalle.html     # Agregar producto a pedido
│   ├── editar_detalle.html      # Editar cantidad de detalle
│   ├── login.html               # Formulario de login
│   └── register.html            # Formulario de registro
├── clientes/
│   ├── listar.html
│   ├── crear.html
│   └── editar.html
└── productos/
    ├── listar.html
    ├── crear.html
    └── editar.html
```

### Ejemplo — Template de listado

```html
{% extends 'base.html' %}

{% block content %}
<div class="card shadow-sm border-0 fixed-list-card">
    <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
        <h5 class="mb-0 fw-semibold">Pedidos</h5>
        <a href="{% url 'crear' %}" class="text-dark text-decoration-none">
            <i class="bi bi-plus-lg"></i> Nuevo Pedido
        </a>
    </div>
    <div class="card-body">
        <table class="table align-middle text-center">
            <thead>
                <tr>
                    <th>ID</th><th>Cliente</th><th>Fecha</th><th>Estado</th><th></th>
                </tr>
            </thead>
            <tbody>
                {% for p in pedidos %}
                <tr>
                    <td>{{ p.id }}</td>
                    <td>{{ p.cliente.nombre }}</td>
                    <td>{{ p.fecha }}</td>
                    <td><span class="badge bg-light text-dark border">{{ p.estado }}</span></td>
                    <td>
                        <a href="/detalle/{{p.id}}"><i class="bi bi-eye"></i> Ver</a>
                        <a href="/editar/{{p.id}}"><i class="bi bi-pencil"></i> Editar</a>
                        <a href="#" onclick="confirmarEliminacion({{p.id}})">
                            <i class="bi bi-trash"></i> Eliminar
                        </a>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="5">No hay pedidos registrados</td></tr>
                {% endfor %}
            </tbody>
        </table>
        <!-- Paginación aquí -->
    </div>
</div>
{% endblock %}
```

---

## 7. Paginación

La paginación está implementada en todas las vistas de listado usando `ListView` de Django.

### Configuración en la vista

```python
class PedidoListView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'pedidos/listar.html'
    context_object_name = 'pedidos'
    paginate_by = 10          # 10 registros por página
    ordering = ['id']
```

### Template de paginación

Agregar al final de la tabla en cada template de listado:

```html
<!-- PAGINACIÓN -->
{% if is_paginated %}
<nav class="mt-3">
    <ul class="pagination pagination-sm justify-content-center mb-0">

        {% if page_obj.has_previous %}
        <li class="page-item">
            <a class="page-link text-dark" href="?page={{ page_obj.previous_page_number }}">
                <i class="bi bi-chevron-left"></i>
            </a>
        </li>
        {% endif %}

        {% for num in paginator.page_range %}
            {% if page_obj.number == num %}
            <li class="page-item active">
                <span class="page-link bg-dark text-white border-0">{{ num }}</span>
            </li>
            {% else %}
            <li class="page-item">
                <a class="page-link text-dark" href="?page={{ num }}">{{ num }}</a>
            </li>
            {% endif %}
        {% endfor %}

        {% if page_obj.has_next %}
        <li class="page-item">
            <a class="page-link text-dark" href="?page={{ page_obj.next_page_number }}">
                <i class="bi bi-chevron-right"></i>
            </a>
        </li>
        {% endif %}

    </ul>
</nav>
{% endif %}
```

### Variables de contexto disponibles

| Variable               | Descripción                              |
|------------------------|------------------------------------------|
| `page_obj`             | Objeto de la página actual               |
| `paginator`            | Objeto paginador con `page_range`        |
| `is_paginated`         | `True` si hay más de una página          |
| `page_obj.has_previous`| Si existe página anterior                |
| `page_obj.has_next`    | Si existe página siguiente               |

---

## 8. SweetAlert2

SweetAlert2 se carga desde CDN en `base.html` y se usa para confirmar eliminaciones antes de ejecutarlas.

### Inclusión del CDN

```html
<!-- base.html <head> -->
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
```

### Función de confirmación (JavaScript)

```html
<script>
function confirmarEliminacion(id) {
    Swal.fire({
        title: '¿Estás seguro?',
        text:  'Esta acción no se puede deshacer.',
        icon:  'warning',
        showCancelButton:  true,
        confirmButtonColor: '#d33',
        cancelButtonColor:  '#6c757d',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText:  'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = '/eliminar/' + id + '/';
        }
    });
}
</script>
```

### Uso en el template

```html
<!-- Botón de eliminar en la tabla -->
<a href="#" onclick="confirmarEliminacion({{ p.id }})">
    <i class="bi bi-trash"></i> Eliminar
</a>
```

### Mostrar mensajes de Django con SweetAlert2

```html
{% if messages %}
<script>
    document.addEventListener('DOMContentLoaded', function () {
        {% for message in messages %}
        Swal.fire({
            icon:  '{{ message.tags }}',
            title: '{{ message }}',
            timer: 2500,
            showConfirmButton: false
        });
        {% endfor %}
    });
</script>
{% endif %}
```

> En Django, los tags de mensajes son: `success`, `error`, `warning`, `info`.

---

## 9. Exportación PDF y Excel

Las funciones de exportación están en `pedidos/reportes.py` y requieren:

- **ReportLab** → generación de PDFs
- **openpyxl** → generación de archivos Excel

### URLs de exportación

```python
path('exportar/pedidos/pdf/',           reportes.exportar_pedidos_pdf),
path('exportar/clientes/pdf/',          reportes.exportar_clientes_pdf),
path('exportar/productos/pdf/',         reportes.exportar_productos_pdf),
path('exportar/detalles/pdf/',          reportes.exportar_detalles_pdf),
path('exportar/todo/excel/',            reportes.exportar_todo_excel),
path('exportar/detalles/excel/',        reportes.exportar_detalles_excel),
path('exportar/clientes/json/',         reportes.exportar_clientes_json),
path('exportar/productos/json/',        reportes.exportar_productos_json),
path('exportar/pedidos/detallado/json/',reportes.exportar_pedidos_detallado_json),
```

### Exportar PDF con ReportLab

```python
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

@login_required
def exportar_pedidos_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="pedidos.pdf"'

    doc      = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles   = getSampleStyleSheet()
    pedidos  = Pedido.objects.all()

    # Encabezado
    elements.append(Paragraph("SISTEMA DE GESTIÓN", styles['Normal']))
    elements.append(Paragraph("REPORTE DE PEDIDOS",  styles['Title']))
    elements.append(Spacer(1, 20))

    # Tabla de datos
    data = [['ID', 'Cliente', 'Fecha', 'Estado']]
    for p in pedidos:
        data.append([p.id, p.cliente.nombre, str(p.fecha), p.estado])

    table = Table(data, colWidths=[50, 150, 120, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(table)

    doc.build(elements)
    return response
```

### Exportar Excel con openpyxl

```python
from openpyxl import Workbook

@login_required
def exportar_todo_excel(request):
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="reporte_completo.xlsx"'

    wb = Workbook()

    # Hoja Pedidos
    ws1 = wb.active
    ws1.title = "Pedidos"
    ws1.append(['ID', 'Cliente', 'Fecha', 'Estado'])
    for p in Pedido.objects.all():
        ws1.append([p.id, p.cliente.nombre, str(p.fecha), p.estado])

    # Hoja Clientes
    ws2 = wb.create_sheet("Clientes")
    ws2.append(['ID', 'Nombre', 'Correo', 'Teléfono'])
    for c in Cliente.objects.all():
        ws2.append([c.id, c.nombre, c.correo, c.telefono])

    wb.save(response)
    return response
```

### Botones de exportación en el template

```html
<div class="d-flex gap-3">
    <a href="/exportar/pedidos/pdf/" class="text-dark small">
        <i class="bi bi-file-earmark-pdf"></i> PDF
    </a>
    <a href="/exportar/todo/excel/" class="text-dark small">
        <i class="bi bi-file-earmark-excel"></i> Excel
    </a>
    <a href="/exportar/pedidos/detallado/json/" class="text-dark small">
        <i class="bi bi-braces"></i> JSON
    </a>
</div>
```

---

## 10. Capturas paso a paso

### Paso 1 — Activar entorno e instalar dependencias

```
(env) PS C:\...\gestion_pedidos3> pip install -r requirements.txt
Successfully installed Django-6.0.3 mysqlclient-2.2.8 openpyxl-3.1.5 ...
```

![Instalación de dependencias](docs/screenshots/01_pip_install.png)

---

### Paso 2 — Crear y aplicar migraciones

```
(env) PS C:\...\gestion_pedidos3> python manage.py makemigrations
Migrations for 'pedidos':
  pedidos\migrations\0001_initial.py
    - Create model Cliente
    - Create model Producto
    - Create model Pedido
    - Create model DetallePedido

(env) PS C:\...\gestion_pedidos3> python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, pedidos, sessions
Running migrations:
  Applying pedidos.0001_initial... OK
```

![Migraciones aplicadas](docs/screenshots/02_migrate.png)

---

### Paso 3 — Iniciar el servidor

```
(env) PS C:\...\gestion_pedidos3> python manage.py runserver
Django version 6.0.3, using settings 'proyecto_pedidos.settings'
Starting development server at http://127.0.0.1:8000/
```

![Servidor en ejecución](docs/screenshots/03_runserver.png)

---

### Paso 4 — Pantalla de Login

Acceder a `http://127.0.0.1:8000/login/`

- El sistema redirige automáticamente al login si no hay sesión activa.
- Tras autenticarse correctamente se genera una cookie JWT (`jwt_token`) con expiración de 1 hora.

![Pantalla de login](docs/screenshots/04_login.png)

---

### Paso 5 — Panel principal — Listado de Pedidos

URL: `http://127.0.0.1:8000/listar/`

- Sidebar con navegación a Pedidos, Clientes, Productos y Detalles.
- Tabla con 10 registros por página.
- Botones de exportación: PDF, Excel, JSON.

![Listado de pedidos](docs/screenshots/05_listar_pedidos.png)

---

### Paso 6 — Crear un nuevo pedido

URL: `http://127.0.0.1:8000/crear/`

- Formulario con cliente, fecha y estado.
- Al guardar exitosamente aparece alerta SweetAlert2 de confirmación.

![Crear pedido](docs/screenshots/06_crear_pedido.png)

---

### Paso 7 — Editar un pedido

URL: `http://127.0.0.1:8000/editar/<id>/`

- Formulario pre-cargado con los datos del pedido.
- Alerta de éxito al guardar.

![Editar pedido](docs/screenshots/07_editar_pedido.png)

---

### Paso 8 — Confirmación de eliminación con SweetAlert2

Al hacer clic en el botón **Eliminar** se muestra un diálogo de confirmación antes de ejecutar la acción.

![SweetAlert2 eliminación](docs/screenshots/08_sweetalert_eliminar.png)

---

### Paso 9 — Listado de Clientes con paginación

URL: `http://127.0.0.1:8000/clientes/`

- Misma estructura de tabla con paginación y botones CRUD.
- Exportación disponible en PDF y JSON.

![Listado de clientes](docs/screenshots/09_listar_clientes.png)

---

### Paso 10 — Agregar detalle a un pedido

URL: `http://127.0.0.1:8000/pedido/<id>/agregar/`

- Selección del producto y cantidad.
- El subtotal se calcula automáticamente (`cantidad × precio`).

![Agregar detalle](docs/screenshots/10_agregar_detalle.png)

---

### Paso 11 — Exportar PDF de pedidos

Hacer clic en el botón **PDF** del listado de pedidos o acceder directamente a:

```
http://127.0.0.1:8000/exportar/pedidos/pdf/
```

El navegador descarga el archivo `pedidos.pdf` con encabezado, fecha de generación y tabla formateada.

![PDF exportado](docs/screenshots/11_pdf_pedidos.png)

---

### Paso 12 — Exportar Excel completo

Hacer clic en el botón **Excel** o acceder a:

```
http://127.0.0.1:8000/exportar/todo/excel/
```

El archivo `reporte_completo.xlsx` incluye hojas separadas para Pedidos, Clientes, Productos y Detalles.

![Excel exportado](docs/screenshots/12_excel_completo.png)

---

## Resumen de tecnologías

| Tecnología      | Versión  | Uso                                  |
|-----------------|----------|--------------------------------------|
| Django          | 6.0.3    | Framework principal                  |
| MySQL           | 8.0+     | Base de datos                        |
| mysqlclient     | 2.2.8    | Conector Python-MySQL                |
| Bootstrap       | 5.3      | Estilos y layout (CDN)               |
| Bootstrap Icons | 1.11     | Iconografía (CDN)                    |
| SweetAlert2     | 11       | Diálogos de confirmación (CDN)       |
| ReportLab       | 4.4.10   | Generación de PDFs                   |
| openpyxl        | 3.1.5    | Generación de archivos Excel         |
| Pillow          | 12.1.1   | Procesamiento de imágenes            |

---

## Comandos rápidos de referencia

```bash
# Activar entorno virtual (Windows)
env\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor de desarrollo
python manage.py runserver
```
