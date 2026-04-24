from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError


class DetalleFactura(models.Model):
    factura = models.ForeignKey(
        'transacciones.Factura',
        on_delete=models.CASCADE,
        related_name="detalles"
    )

    producto = models.ForeignKey(
        'inventario.Producto', null=True, blank=True, on_delete=models.SET_NULL
    )
    servicio = models.ForeignKey(
        'citas.Servicio', null=True, blank=True, on_delete=models.SET_NULL
    )

    descripcion = models.CharField(max_length=255, blank=True)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        verbose_name = "Detalle de Factura"
        verbose_name_plural = "Detalles de Factura"

    # ----------------------------
    # VALIDACIONES
    # ----------------------------
    def clean(self):
        # SOLO producto XOR servicio
        if (self.producto and self.servicio) or (not self.producto and not self.servicio):
            raise ValidationError("Debe especificar exactamente un producto o un servicio.")

        # Autodescripción
        if self.producto and not self.descripcion:
            self.descripcion = str(self.producto.descripcion)

        if self.servicio and not self.descripcion:
            # Ajusta si tu servicio tiene otro nombre del campo
            self.descripcion = str(getattr(self.servicio, "nombre", "Servicio"))

    # ----------------------------
    # SUBTOTAL
    # ----------------------------
    def calcular_subtotal(self):
        self.subtotal = (self.precio_unitario or Decimal('0.00')) * Decimal(self.cantidad or 1)

    # ----------------------------
    # SAVE
    # ----------------------------
    def save(self, *args, **kwargs):

        # Asignar precio desde Producto si no se envió
        if not self.precio_unitario or self.precio_unitario == 0:
            if self.producto:
                self.precio_unitario = self.producto.precio_venta

            if self.servicio:
                # Ajusta si tu servicio usa otro campo
                precio_servicio = getattr(self.servicio, "costo", None)
                if precio_servicio:
                    self.precio_unitario = precio_servicio

        # Asegurar descripción
        if self.producto and not self.descripcion:
            self.descripcion = str(self.producto.descripcion)

        if self.servicio and not self.descripcion:
            self.descripcion = str(getattr(self.servicio, "nombre", "Servicio"))

        # Validación final
        self.full_clean()

        # Calcular subtotal
        self.calcular_subtotal()

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.descripcion} x{self.cantidad} - Factura {self.factura_id}"