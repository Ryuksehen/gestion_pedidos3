# ─────────────────────────────────────────────────────────
# reportes.py
# Genera reportes descargables en PDF, Excel y JSON.
# Todos los endpoints requieren autenticación.
# PDF  → ReportLab (SimpleDocTemplate + Table)
# Excel → openpyxl (Workbook con múltiples hojas)
# JSON  → JsonResponse de Django (datos serializados a mano)
# ─────────────────────────────────────────────────────────
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from datetime import datetime

# ReportLab: librería para generación de documentos PDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

# Openpyxl: librería para generar archivos Excel (.xlsx)
from openpyxl import Workbook

# Modelos que se exportarán en los reportes
from .models import Pedido, Cliente, Producto, DetallePedido

# ─────────────────────────────────────────────────────────
# REPORTES EN PDF
# Cada función sigue el mismo patrón:
#   1. Crear el HttpResponse con content_type PDF
#   2. Construir el documento con SimpleDocTemplate
#   3. Agregar párrafos (título, fecha, totales) y la tabla de datos
#   4. Cerrar el documento con doc.build(elements)
# ─────────────────────────────────────────────────────────

@login_required
def exportar_pedidos_pdf(request):
    # Crear la respuesta HTTP con el tipo MIME correcto para PDF
    response = HttpResponse(content_type='application/pdf')
    # Content-Disposition 'attachment' fuerza al navegador a descargar el archivo
    response['Content-Disposition'] = 'attachment; filename="pedidos.pdf"'

    # SimpleDocTemplate gestiona márgenes y el flujo del documento
    doc      = SimpleDocTemplate(response, pagesize=letter)
    elements = []              # Lista de elementos que se insertarán en el PDF
    styles   = getSampleStyleSheet()  # Estilos predefinidos de ReportLab
    pedidos  = Pedido.objects.all()   # Obtener todos los pedidos

    # ENCABEZADO
    elements.append(Paragraph("SISTEMA DE GESTIÓN", styles['Normal']))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("REPORTE DE PEDIDOS", styles['Title']))
    elements.append(Spacer(1, 10))

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    elements.append(Paragraph(f"Fecha de generación: {fecha}", styles['Normal']))
    elements.append(Paragraph(f"Total de pedidos: {pedidos.count()}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # TABLA
    data = [['ID', 'Cliente', 'Fecha', 'Estado']]
    for p in pedidos:
        data.append([
            p.id,
            p.cliente.nombre,
            str(p.fecha),
            p.estado
        ])

    table = Table(data, colWidths=[50, 150, 120, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)

    # PIE DE PÁGINA
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Documento generado automáticamente por el sistema", styles['Italic']))

    doc.build(elements)
    return response


@login_required
def exportar_clientes_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="clientes.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    clientes = Cliente.objects.all()

    # ENCABEZADO
    elements.append(Paragraph("SISTEMA DE GESTIÓN", styles['Normal']))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("REPORTE DE CLIENTES", styles['Title']))
    elements.append(Spacer(1, 10))

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    elements.append(Paragraph(f"Fecha de generación: {fecha}", styles['Normal']))
    elements.append(Paragraph(f"Total de clientes: {clientes.count()}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # TABLA
    data = [['ID', 'Nombre', 'Correo', 'Teléfono']]
    for c in clientes:
        data.append([
            c.id,
            c.nombre,
            c.correo,
            c.telefono
        ])

    table = Table(data, colWidths=[50, 150, 200, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)

    # PIE
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Documento generado automáticamente por el sistema", styles['Italic']))

    doc.build(elements)
    return response


@login_required
def exportar_productos_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="productos.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    productos = Producto.objects.all()

    # ENCABEZADO
    elements.append(Paragraph("SISTEMA DE GESTIÓN", styles['Normal']))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("REPORTE DE PRODUCTOS", styles['Title']))
    elements.append(Spacer(1, 10))

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    elements.append(Paragraph(f"Fecha de generación: {fecha}", styles['Normal']))
    elements.append(Paragraph(f"Total de productos: {productos.count()}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # TABLA
    data = [['ID', 'Nombre', 'Precio', 'Stock']]
    for p in productos:
        data.append([
            p.id,
            p.nombre,
            str(p.precio),
            p.stock
        ])

    table = Table(data, colWidths=[50, 180, 100, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)

    # PIE
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Documento generado automáticamente por el sistema", styles['Italic']))

    doc.build(elements)
    return response


@login_required
def exportar_detalles_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="detalles.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    detalles = DetallePedido.objects.all()

    # ENCABEZADO
    elements.append(Paragraph("SISTEMA DE GESTIÓN", styles['Normal']))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("REPORTE DE TODOS LOS DETALLES", styles['Title']))
    elements.append(Spacer(1, 10))

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    elements.append(Paragraph(f"Fecha de generación: {fecha}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # TABLA
    data = [['Ped#', 'Cliente', 'Producto', 'Cant', 'Subtotal']]
    for d in detalles:
        data.append([
            d.pedido.id,
            d.pedido.cliente.nombre,
            d.producto.nombre,
            d.cantidad,
            str(d.subtotal)
        ])

    table = Table(data, colWidths=[40, 120, 180, 50, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)

    # PIE
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Documento generado automáticamente por el sistema", styles['Italic']))

    doc.build(elements)
    return response


# ─────────────────────────────────────────────────────────
# REPORTE EXCEL CONSOLIDADO
# Genera un único archivo .xlsx con múltiples hojas:
#   Hoja 1: Pedidos   Hoja 2: Clientes   Hoja 3: Productos
# ─────────────────────────────────────────────────────────

@login_required
def exportar_todo_excel(request):
    # Tipo MIME para archivos Excel modernos (.xlsx)
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=reportes.xlsx'

    wb = Workbook()  # Crear un libro de trabajo nuevo

    # HOJA 1: PEDIDOS
    ws1 = wb.active      # La primera hoja se obtiene con wb.active
    ws1.title = "Pedidos"
    ws1.append(['ID', 'Cliente', 'Fecha', 'Estado'])  # Fila de encabezados
    for p in Pedido.objects.all():
        ws1.append([p.id, p.cliente.nombre, str(p.fecha), p.estado])

    # HOJA 2: CLIENTES
    ws2 = wb.create_sheet(title="Clientes")  # Crear una hoja adicional
    ws2.append(['ID', 'Nombre', 'Correo', 'Teléfono'])
    for c in Cliente.objects.all():
        ws2.append([c.id, c.nombre, c.correo, c.telefono])

    # HOJA 3: PRODUCTOS
    ws3 = wb.create_sheet(title="Productos")
    ws3.append(['ID', 'Nombre', 'Precio', 'Stock'])
    for p in Producto.objects.all():
        ws3.append([p.id, p.nombre, p.precio, p.stock])

    wb.save(response)  # Escribir el libro directamente en el HttpResponse
    return response


@login_required
def exportar_detalles_excel(request):
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=detalles.xlsx'

    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Todos los Detalles"
    ws1.append(['ID Detalle', 'Pedido', 'Cliente', 'Producto', 'Cantidad', 'Subtotal'])
    for d in DetallePedido.objects.all():
        ws1.append([d.id, d.pedido.id, d.pedido.cliente.nombre, d.producto.nombre, d.cantidad, d.subtotal])

    wb.save(response)
    return response


# REPORTES JSON
# Devuelven los datos serializados como JSON usando JsonResponse.
# safe=False permite serializar listas (no solo diccionarios).

@login_required
def exportar_pedidos_detallado_json(request):
    pedidos = Pedido.objects.all()
    data = []
    for p in pedidos:
        detalles = []
        for d in p.detallepedido_set.all():
            detalles.append({
                'producto': d.producto.nombre,
                'cantidad': d.cantidad,
                'subtotal': float(d.subtotal)
            })
        data.append({
            'id': p.id,
            'cliente': p.cliente.nombre,
            'fecha': str(p.fecha),
            'estado': p.estado,
            'detalles': detalles
        })
    return JsonResponse(data, safe=False)


@login_required
def exportar_clientes_json(request):
    clientes = Cliente.objects.all()
    data = []
    for c in clientes:
        data.append({
            'id': c.id,
            'nombre': c.nombre,
            'correo': c.correo,
            'telefono': c.telefono
        })
    return JsonResponse(data, safe=False)


@login_required
def exportar_productos_json(request):
    productos = Producto.objects.all()
    data = []
    for p in productos:
        data.append({
            'id': p.id,
            'nombre': p.nombre,
            'precio': float(p.precio),
            'stock': p.stock
        })
    return JsonResponse(data, safe=False)
