"""
UsuarioPendiente model - Almacena usuarios en proceso de verificación.

Contiene TODOS los datos necesarios para crear un Usuario completo,
incluyendo los campos del perfil Cliente.
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta
from common.models import BaseModel


class UsuarioPendiente(BaseModel):
    """
    Modelo que almacena usuarios pendientes de verificación por email.
    
    Contiene todos los datos necesarios para crear tanto el Usuario
    como su perfil Cliente asociado una vez verificado.
    """
    
    # Campos del Usuario
    username = models.CharField('Nombre de usuario', max_length=150, unique=True)
    email = models.EmailField('Correo electrónico', unique=True)
    password = models.CharField('Contraseña hasheada', max_length=255)
    nombre = models.CharField('Nombre', max_length=100)
    apellido = models.CharField('Apellido', max_length=100)
    
    # Campos del perfil Cliente (opcionales)
    telefono = models.CharField('Teléfono', max_length=20, blank=True, default='')
    direccion = models.TextField('Dirección', blank=True, default='')
    
    # Campos de verificación
    verification_code = models.CharField('Código de verificación', max_length=6)
    code_expires_at = models.DateTimeField('Código expira en')
    
    # Contador de intentos de verificación (seguridad adicional)
    intentos_verificacion = models.IntegerField('Intentos de verificación', default=0)

    class Meta:
        db_table = 'usuarios_pendientes'
        verbose_name = 'Usuario Pendiente'
        verbose_name_plural = 'Usuarios Pendientes'
        ordering = ['-created_at']

    def __str__(self):
        return f"Pendiente: {self.email} ({self.username})"
    
    def es_codigo_valido(self) -> bool:
        """
        Verifica si el código de verificación sigue siendo válido.
        
        Returns:
            bool: True si el código no ha expirado (20 minutos desde creación).
        """
        ahora = timezone.now()
        return ahora <= self.code_expires_at
    
    def incrementar_intentos(self) -> int:
        """
        Incrementa el contador de intentos de verificación fallidos.
        
        Returns:
            int: Número actual de intentos.
        """
        self.intentos_verificacion += 1
        self.save(update_fields=['intentos_verificacion'])
        return self.intentos_verificacion
    
    def resetear_intentos(self) -> None:
        """Resetea el contador de intentos de verificación."""
        self.intentos_verificacion = 0
        self.save(update_fields=['intentos_verificacion'])
    
    @property
    def max_intentos_excedidos(self) -> bool:
        """Verifica si se excedió el máximo de intentos (ej: 5)."""
        return self.intentos_verificacion >= 5