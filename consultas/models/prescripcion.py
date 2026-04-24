from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

class Prescripcion(models.Model):
    """
    Medicamentos recetados durante una consulta, asociados al inventario.
    """
    consulta = models.ForeignKey(
        'Consulta',
        on_delete=models.CASCADE,
        related_name='prescripciones',
        verbose_name=_("Consulta")
    )

    medicamento = models.ForeignKey(
        'inventario.Producto',
        on_delete=models.PROTECT,
        verbose_name=_("Medicamento"),
        related_name='prescripciones',
    )

    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Cantidad"),
    )

    indicaciones = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Indicaciones de uso"),
    )

    fecha_prescripcion = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Fecha de prescripción")
    )

    class Meta:
        verbose_name = _("Prescripción")
        verbose_name_plural = _("Prescripciones")
        ordering = ['fecha_prescripcion']
        indexes = [
            models.Index(fields=['medicamento']),
            models.Index(fields=['-fecha_prescripcion']),
        ]

    def __str__(self):
        return f"{self.medicamento.descripcion} - Cantidad: {self.cantidad}"

    def clean(self):
        """
        Validaciones básicas de cantidad e inventario.
        """
        super().clean()

        if not self.medicamento:
            raise ValidationError({
                'medicamento': _("Debe seleccionar un medicamento del inventario")
            })

        if self.cantidad < 1:
            raise ValidationError({
                'cantidad': _("La cantidad debe ser al menos 1")
            })