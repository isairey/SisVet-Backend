from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from usuarios.models import Veterinario

class Consulta(models.Model):
    """
    Consulta veterinaria completa, con los datos de la mascota y el veterinario.
    """

    cita = models.OneToOneField(
        'citas.Cita',  # Referencia a la Cita origen
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consulta_generada',
        verbose_name=_("Cita de origen")
    )

    servicio = models.ForeignKey(
        'citas.Servicio',  # Referencia por string al modelo Servicio
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultas',
        verbose_name=_("Servicio realizado")
    )

    mascota = models.ForeignKey(
        'mascotas.Mascota',
        on_delete=models.CASCADE,
        related_name='consultas',
        verbose_name=_("Mascota"),
    )


    veterinario = models.ForeignKey(
        Veterinario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='consultas_atendidas',
        verbose_name=_("Veterinario"),
    )

    fecha_consulta = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Fecha de consulta")
    )

    descripcion_consulta = models.TextField(
        verbose_name=_("Descripción de la consulta"),
    )

    diagnostico = models.TextField(
        verbose_name=_("Diagnóstico"),
    )

    notas_adicionales = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Notas adicionales"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de creación")
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Última actualización")
    )

    consentimiento_token = models.CharField(
        max_length=64,
        editable=False,
        null=True,
        blank=True,
        unique=True,
        verbose_name=_("Token de Consentimiento")
    )
    consentimiento_otorgado = models.BooleanField(
        default=False,
        verbose_name=_("Consentimiento Otorgado")
    )
    consentimiento_fecha = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Fecha de Consentimiento")
    )

    class Meta:
        verbose_name = _("Consulta")
        verbose_name_plural = _("Consultas")
        ordering = ['-fecha_consulta']
        indexes = [
            models.Index(fields=['-fecha_consulta']),
            models.Index(fields=['veterinario']),
            models.Index(fields=['mascota']),
        ]

    def __str__(self):
        return f"Consulta {self.mascota.nombre} - {self.fecha_consulta.strftime('%d/%m/%Y')}"

    def clean(self):
        """
        Validaciones mínimas de campos requeridos.
        """
        super().clean()

        if not self.descripcion_consulta or self.descripcion_consulta.strip() == '':
            raise ValidationError({
                'descripcion_consulta': _("La descripción de la consulta es obligatoria")
            })
        if not self.diagnostico or self.diagnostico.strip() == '':
            raise ValidationError({
                'diagnostico': _("Debe ingresar un diagnóstico")
            })

        if self.consentimiento_otorgado and not self.consentimiento_fecha:
            self.consentimiento_fecha = timezone.now()

    def get_prescripciones_count(self):
        """Devuelve el número de prescripciones asociadas a esta consulta"""
        return self.prescripciones.count()

    def get_examenes_count(self):
        """Devuelve el número de exámenes asociados a esta consulta"""
        return self.examenes.count()

    def get_estado_vacunacion_consulta(self):
        """Obtiene el estado de vacunación registrado en la consulta"""
        historial = self.vacunas.last()
        if historial:
            return historial.get_estado_display()
        return "No registrado"