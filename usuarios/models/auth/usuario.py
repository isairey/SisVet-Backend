"""
Usuario model - Representa el usuario del sistema con autenticación personalizada.
Gestiona autenticación, roles y seguridad de intentos fallidos.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta
from common.models import BaseModel
from usuarios.manager import UserManager


class Usuario(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Modelo base de Usuario del sistema.

    - Extiende AbstractBaseUser para autenticación personalizada.
    - Gestiona autenticación y roles.
    - Controla intentos fallidos y bloqueos temporales por seguridad.

    Autor: Jeronimo Rodriguez (10/28/2025)
    """
    
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido'),
    ]
    
    # Campos básicos
    nombre = models.CharField('Nombre', max_length=100)
    apellido = models.CharField('Apellido', max_length=100)
    email = models.EmailField('Correo electrónico', unique=True)
    username = models.CharField(
        'Nombre de usuario',
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='El nombre de usuario solo puede contener letras, números y @/./+/-/_'
        )]
    )
    password = models.CharField(max_length=255)
    
    # Estado y control
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default='activo')
    is_staff = models.BooleanField('Es staff', default=False)
    is_active = models.BooleanField('Está activo', default=True)

    # Campos adicionales para manejar seguridad de intentos de inicio de sesión
    intentos_fallidos = models.IntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'nombre', 'apellido']
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.username})"
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario."""
        return f"{self.nombre} {self.apellido}"
    
    def esta_bloqueado(self) -> bool:
        """
        Verifica si el usuario está temporalmente bloqueado debido a múltiples 
        intentos fallidos de autenticación.
        
        Returns:
            bool: True si el usuario está bloqueado, False en caso contrario.
        """
        if self.bloqueado_hasta and timezone.now() < self.bloqueado_hasta:
            return True
        return False

    def registrar_intento_fallido(self, max_intentos: int = 5, minutos_bloqueo: int = 10) -> str:
        """
        Incrementa el contador de intentos fallidos y bloquea al usuario 
        temporalmente si supera el número máximo permitido.

        Args:
            max_intentos (int): Cantidad máxima de intentos antes del bloqueo.
            minutos_bloqueo (int): Duración del bloqueo temporal en minutos.

        Returns:
            str: Mensaje indicando el estado actual (intentos restantes o bloqueo activo).
        """
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= max_intentos:
            self.bloqueado_hasta = timezone.now() + timedelta(minutes=minutos_bloqueo)
            self.intentos_fallidos = 0  # reset después de bloquear
            self.save()
            return f"Cuenta bloqueada temporalmente por {minutos_bloqueo} minutos."

        self.save()
        intentos_restantes = max_intentos - self.intentos_fallidos
        return f"Credenciales incorrectas. Intentos restantes: {intentos_restantes}"

    def resetear_intentos(self) -> None:
        """
        Restablece los contadores de seguridad después de un inicio de sesión exitoso.

        - Limpia el número de intentos fallidos.
        - Elimina cualquier bloqueo temporal activo.
        """
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
        self.save()


from .usuario_pendiente import UsuarioPendiente  # re-export for backward compatibility
