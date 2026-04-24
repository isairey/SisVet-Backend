"""
inventario/admin.py - VERSIÓN SIN DUPLICADOS
"""
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.html import format_html

from .models import Marca, Categoria, Producto, Kardex, Notificacion
from inventario.services.producto_service import ProductoService
from inventario.patrones import InventarioProxy, GestorInventario


# ==================== PRODUCTO ====================
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "marca",
        "categoria",
        "stock",
        "stock_minimo",
        "precio_venta",
        "fecha_vencimiento",
        "activo",
    )
    list_filter = ("marca", "categoria", "activo")
    search_fields = ("nombre", "descripcion", "codigo_barras", "codigo_interno")

    fields = (
        "nombre",
        "descripcion",
        "marca",
        "categoria",
        "stock",
        "stock_minimo",
        "codigo_barras",
        "codigo_interno",
        "precio_venta",
        "precio_compra",
        "fecha_vencimiento",
        "activo",
    )

    def save_model(self, request, obj, form, change):
        """
        Guarda el producto con validaciones del ProductoService.
        """
        service = ProductoService()
        data = form.cleaned_data

        # Validar datos
        errores = service.validar_datos_producto(
            data, producto_id=obj.pk if change else None
        )

        if errores:
            campo = errores.get("campo", None)
            mensaje = errores["mensaje"]

            if campo and campo in form.fields:
                form.add_error(campo, mensaje)
            else:
                form.add_error(None, mensaje)

            raise ValidationError(mensaje)

        # Normalizar datos
        normalizados = service.normalizar_datos_producto(data)
        for key, value in normalizados.items():
            setattr(obj, key, value)

        # Guardar UNA SOLA VEZ
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        """Permite mostrar el botón eliminar."""
        return True

    def delete_model(self, request, obj):
        """
        SOFT DELETE: Marca como INACTIVO en lugar de eliminar.

        Cuando presiones "Eliminar":
        - El producto NO se borra de la BD
        - Solo se marca como activo=False
        - No se pueden crear nuevos movimientos
        """
        obj.activo = False
        obj.save(update_fields=["activo"])

        from django.contrib import messages
        messages.success(
            request,
            f"Producto '{obj.nombre}' desactivado. Ya no se pueden hacer movimientos."
        )

    def delete_queryset(self, request, queryset):
        """Soft delete en masa."""
        for obj in queryset:
            obj.activo = False
            obj.save(update_fields=["activo"])

    # URLs personalizadas para acciones con Patrones
    def get_urls(self):
        """Agrega URLs personalizadas para las acciones admin."""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:producto_id>/ajustar-stock/',
                self.admin_site.admin_view(self.ajustar_stock_view),
                name='producto-ajustar-stock',
            ),
            path(
                '<int:producto_id>/conteo-fisico/',
                self.admin_site.admin_view(self.conteo_fisico_view),
                name='producto-conteo-fisico',
            ),
        ]
        return custom_urls + urls

    def ajustar_stock_view(self, request, producto_id):
        """Vista admin para ajustar stock usando InventarioProxy."""
        producto = self.get_object(request, producto_id)

        if producto is None:
            messages.error(request, 'Producto no encontrado')
            return redirect('admin:inventario_producto_changelist')

        if request.method == 'POST':
            try:
                cantidad = float(request.POST.get('cantidad'))
                motivo = request.POST.get('motivo', 'Ajuste manual desde admin')

                proxy = InventarioProxy(usuario=request.user)
                resultado = proxy.modificar_stock(
                    producto=producto,
                    cantidad=cantidad,
                    motivo=motivo
                )

                messages.success(
                    request,
                    f'Stock ajustado: {resultado["stock_anterior"]} → {resultado["stock_nuevo"]}'
                )
                return redirect('admin:inventario_producto_change', producto.pk)

            except PermissionError as e:
                messages.error(request, f'Error de permisos: {e}')
            except ValueError as e:
                messages.error(request, f'Error: {e}')
            except Exception as e:
                messages.error(request, f'Error inesperado: {e}')

        context = {
            'producto': producto,
            'title': f'Ajustar Stock: {producto.nombre}',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }

        return render(request, 'admin/inventario/ajustar_stock.html', context)

    def conteo_fisico_view(self, request, producto_id):
        """Vista admin para conteo físico usando InventarioProxy."""
        producto = self.get_object(request, producto_id)

        if producto is None:
            messages.error(request, 'Producto no encontrado')
            return redirect('admin:inventario_producto_changelist')

        if request.method == 'POST':
            try:
                stock_real = float(request.POST.get('stock_real'))
                motivo = request.POST.get('motivo', 'Conteo físico desde admin')

                proxy = InventarioProxy(usuario=request.user)
                resultado = proxy.ajustar_inventario(
                    producto=producto,
                    stock_real=stock_real,
                    motivo=motivo
                )

                messages.success(
                    request,
                    f'Inventario ajustado. Diferencia: {resultado["diferencia"]} ({resultado["tipo_ajuste"]})'
                )
                return redirect('admin:inventario_producto_change', producto.pk)

            except PermissionError as e:
                messages.error(request, f'Error de permisos: {e}')
            except Exception as e:
                messages.error(request, f'Error: {e}')

        context = {
            'producto': producto,
            'title': f'Conteo Físico: {producto.nombre}',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }

        return render(request, 'admin/inventario/conteo_fisico.html', context)

# ==================== KARDEX ====================
@admin.register(Kardex)
class KardexAdmin(admin.ModelAdmin):
    list_display = (
        'codigo_interno_producto',
        "producto",
        "tipo",
        "cantidad",
        "detalle",
        "fecha"
    )
    list_filter = ["tipo", "fecha"]
    search_fields = ["detalle", "producto__nombre", 'producto__codigo_interno']
    readonly_fields = ('fecha',)

    def get_readonly_fields(self, request, obj=None):
        """
        Si estamos EDITANDO, bloquear campos críticos.
        Si estamos CREANDO, solo fecha es readonly.
        """
        if obj:  # Editar
            return ('fecha', 'producto', 'tipo', 'cantidad')
        return ('fecha',)  # Crear

    def codigo_interno_producto(self, obj):
        return obj.producto.codigo_interno or '---'

    codigo_interno_producto.short_description = 'Código Interno'

    def save_model(self, request, obj, form, change):
        """
        Valida que el producto esté activo antes de guardar.
        El signal post_save se encarga de procesar el movimiento.
        """
        from django.core.exceptions import ValidationError
        from inventario.validators.kardex_validator import KardexValidator

        # Si es NUEVO (change=False), validar que el producto esté activo
        if not change:
            validator = KardexValidator()
            try:
                validator.validar_producto_activo(obj.producto)
            except ValidationError as e:
                form.add_error('producto', str(e))
                raise ValidationError(str(e))

        # Guardar el Kardex
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return True

    def delete_model(self, request, obj):
        """Soft delete: anula el movimiento."""
        obj.delete()

    def delete_queryset(self, request, queryset):
        """Anula múltiples registros."""
        for obj in queryset:
            obj.delete()

# ==================== MARCA ====================
@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ("descripcion",)
    search_fields = ("descripcion",)


# ==================== CATEGORIA ====================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("descripcion", "mostrar_color")
    search_fields = ("descripcion",)

    def mostrar_color(self, obj):
        """Muestra el color como un cuadro en lugar de texto."""
        if obj.color:
            return format_html(
                '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #000;"></div>',
                obj.color
            )
        return '-'

    mostrar_color.short_description = 'Color'


# ==================== NOTIFICACION ====================
@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "modulo", "nivel", "leida", "fecha")
    list_filter = ("modulo", "nivel", "leida", "fecha")
    search_fields = ("titulo", "mensaje")
    readonly_fields = ("fecha",)
