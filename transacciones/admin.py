from django.contrib import admin
from .models.factura import Factura
from .models.detalle_factura import DetalleFactura
from .models.pago import Pago
from .models.metodo_pago import MetodoPago

# Register your models here.

class DetalleInline(admin.TabularInline):
    model = DetalleFactura
    extra = 1
    readonly_fields = ('subtotal',)

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'total', 'pagada', 'estado', 'cita', 'consulta')
    inlines = [DetalleInline]

admin.site.register(Pago)
admin.site.register(MetodoPago)
