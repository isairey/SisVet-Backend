from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal

class Factura(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADA', 'Pagada'),
        ('ANULADA', 'Anulada'),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="facturas"
    )
    fecha = models.DateTimeField(default=timezone.now)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    impuestos = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    pagada = models.BooleanField(default=False)

    # opcional vínculo con cita o consulta
    cita = models.ForeignKey('citas.Cita', null=True, blank=True, on_delete=models.SET_NULL)
    consulta = models.ForeignKey('consultas.Consulta', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Factura #{self.id} - Cliente {self.cliente}"

    def recalcular_totales(self):
        """
        Recalcula subtotal (sumatoria de subtotales de detalles), impuestos y total.
        Ajusta reglas de impuestos sencillas (por ejemplo, 0 si no aplica).
        """
        detalles = self.detalles.all()
        subtotal = sum((d.subtotal for d in detalles), Decimal('0.00'))
        # Ajusta esta lógica de impuestos según reglas locales (ejemplo 0%)
        impuestos = Decimal('0.00')
        total = subtotal + impuestos
        # Guardar sin disparar recálculos infinitos
        self.subtotal = subtotal
        self.impuestos = impuestos
        self.total = total
        self.save(update_fields=['subtotal', 'impuestos', 'total'])