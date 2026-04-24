from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class HistorialVacuna(models.Model):
    """
    Registro de vacunas aplicadas o prescritas durante una consulta.
    """

    ESTADO_CHOICES = [
        ('AL_DIA', 'Al día'),
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En proceso'),
        ('NINGUNA', 'Ninguna'),
    ]

    consulta = models.ForeignKey(
        'Consulta',
        on_delete=models.CASCADE,
        related_name='vacunas',
        verbose_name=_("Consulta"),
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        verbose_name=_("Estado de vacunación"),
    )

    vacunas_descripcion = models.TextField(
        verbose_name=_("Vacunas pendientes/aplicadas"),
        blank=True,
        null=True,
        default=""
    )

    fecha_registro = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Fecha de registro")
    )

    class Meta:
        verbose_name = _("Historial de Vacuna")
        verbose_name_plural = _("Historial de Vacunas")
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['-fecha_registro']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        estado_display = self.get_estado_display()
        if self.vacunas_descripcion:
            return f"{estado_display} - {self.vacunas_descripcion[:50]}"
        return f"{estado_display}"

    def clean(self):
        """
        Validaciones básicas de los campos según el estado seleccionado.
        """
        super().clean()

        if self.estado in ['PENDIENTE', 'EN_PROCESO']:
            if not self.vacunas_descripcion or self.vacunas_descripcion.strip() == '':
                raise ValidationError({
                    'vacunas_descripcion': _(
                        'Debe especificar las vacunas cuando el estado es "{}"'
                    ).format(self.get_estado_display())
                })

        if self.estado in ['AL_DIA', 'NINGUNA']:
            self.vacunas_descripcion = ""
