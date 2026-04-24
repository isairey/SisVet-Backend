from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from consultas.models import vacunas

class HistoriaClinica(models.Model):
    """
    Historia clínica consolidada de una mascota.
    """
    mascota = models.OneToOneField(
        'mascotas.Mascota',
        on_delete=models.CASCADE,
        related_name='historias_consulta',
        verbose_name=_("Mascota"),
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de creación de la historia")
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Última actualización")
    )

    estado_vacunacion_actual = models.CharField(
        max_length=20,
        choices=vacunas.HistorialVacuna.ESTADO_CHOICES,
        default='',
        verbose_name=_("Estado de vacunación actual"),
    )

    class Meta:
        verbose_name = _("Historia Clínica")
        verbose_name_plural = _("Historias Clínicas")
        ordering = ['-fecha_actualizacion']
        indexes = [
            models.Index(fields=['mascota']),
            models.Index(fields=['-fecha_actualizacion']),
        ]

    def __str__(self):
        return f"Historia Clínica - {self.mascota.nombre}"

    def get_total_consultas(self):
        """
        Retorna el total de consultas asociadas a la mascota de esta historia clínica.
        """
        return self.mascota.consultas.count()