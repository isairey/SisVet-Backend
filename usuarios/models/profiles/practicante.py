"""
Practicante profile model (separado).
"""
from django.db import models
from django.conf import settings


class Practicante(models.Model):
    """
    Perfil extendido para usuarios practicantes.
    
    Complementa la información del Usuario con detalles específicos del practicante.

    Autor: Jeronimo Rodriguez (10/30/2025)
    """
    
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='perfil_practicante'
    )
    tutor_veterinario = models.ForeignKey(
        'usuarios.Veterinario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='practicantes'
    )
    universidad = models.CharField('Universidad', max_length=200, blank=True)
    periodo_practica = models.CharField('Período de práctica', max_length=100, blank=True)

    class Meta:
        db_table = 'practicantes'
        verbose_name = 'Practicante'
        verbose_name_plural = 'Practicantes'

    def __str__(self):
        return f"Practicante {self.usuario.get_full_name()}"
