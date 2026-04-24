"""
Cliente profile model (separado).
"""
from django.db import models
from django.conf import settings


class Cliente(models.Model):
    """
    Perfil extendido para usuarios clientes (propietarios de mascotas).
    
    Complementa la información del Usuario con detalles específicos del cliente.

    Autor: Jeronimo Rodriguez (10/30/2025)
    """
    
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='perfil_cliente'
    )
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    direccion = models.TextField('Dirección', blank=True)

    class Meta:
        db_table = 'clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.usuario.get_full_name()
