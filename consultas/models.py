from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from usuarios.models import Veterinario

"""
Módulo de Gestión de Consultas y Historias Clínicas
Sara Sanchez
02 Noviembre 2025
"""

User = get_user_model()
# HISTORIAL DE VACUNAS

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

# PRESCRIPCIÓN DE MEDICAMENTOS

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

# EXÁMENES MÉDICOS

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

# CONSULTA

class Consulta(models.Model):
    """
    Consulta veterinaria completa, con los datos de la mascota y el veterinario.
    """
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

# HISTORIA CLÍNICA
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
        choices=HistorialVacuna.ESTADO_CHOICES,
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
