from django.db import models
from django.utils import timezone
from .factura import Factura
from .metodo_pago import MetodoPago


class Pago(models.Model):
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name="pagos"
    )
    metodo = models.ForeignKey(
        MetodoPago,
        on_delete=models.SET_NULL,
        null=True
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(default=timezone.now)
    aprobado = models.BooleanField(default=False)
    referencia = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Pago #{self.id} - Factura {self.factura.id}"