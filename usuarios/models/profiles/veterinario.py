"""
Veterinario profile model (separado).
"""
from django.db import models
from django.conf import settings


class Veterinario(models.Model):
    """
    Perfil extendido para usuarios veterinarios.
    
    Complementa la información del Usuario con detalles específicos del veterinario.

    Autor: Jeronimo Rodriguez (10/30/2025)
    """
    
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='perfil_veterinario'
    )
    licencia = models.CharField('Número de licencia', max_length=50, unique=True)
    especialidad = models.CharField('Especialidad', max_length=100, blank=True)
    horario = models.TextField('Horario de atención', blank=True)

    class Meta:
        db_table = 'veterinarios'
        verbose_name = 'Veterinario'
        verbose_name_plural = 'Veterinarios'

    def __str__(self):
        nombre = self.usuario.get_full_name().strip() if self.usuario else "Sin nombre"
        if nombre:
            return f"Dr(a). {nombre}"
        return f"Dr(a). {self.especialidad or 'Veterinario/a'}"
