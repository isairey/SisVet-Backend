from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Examen(models.Model):
    """
    Exámenes médicos asociados a una consulta.
    """
    TIPO_EXAMEN_CHOICES = [
        ('HEMOGRAMA', 'Hemograma completo'),
        ('QUIMICA_SANGUINEA', 'Química sanguínea'),
        ('URINALISIS', 'Urianálisis'),
        ('COPROLOGICO', 'Coprológico'),
        ('RAYOS_X', 'Rayos X'),
        ('ECOGRAFIA', 'Ecografía'),
        ('CITOLOGIA', 'Citología'),
        ('BIOPSIA', 'Biopsia'),
        ('ELECTROCARDIOGRAMA', 'Electrocardiograma'),
        ('OTRO', 'Otro'),
    ]

    consulta = models.ForeignKey(
        'Consulta',
        on_delete=models.CASCADE,
        related_name='examenes',
        verbose_name=_("Consulta")
    )

    tipo_examen = models.CharField(
        max_length=50,
        choices=TIPO_EXAMEN_CHOICES,
        verbose_name=_("Tipo de examen")
    )

    descripcion = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Descripción adicional"),
    )

    fecha_orden = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Fecha de orden")
    )

    class Meta:
        verbose_name = _("Examen")
        verbose_name_plural = _("Exámenes")
        ordering = ['tipo_examen']
        indexes = [
            models.Index(fields=['tipo_examen']),
        ]

    def __str__(self):
        return f"{self.get_tipo_examen_display()}"