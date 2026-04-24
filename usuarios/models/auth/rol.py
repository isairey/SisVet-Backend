"""
Rol model - Define los roles del sistema y sus asignaciones a usuarios.
Implementa el patrón RBAC (Role-Based Access Control).
"""
from django.db import models
from django.conf import settings
from common.models import BaseModel


class Rol(models.Model):
    """
    Modelo de roles del sistema.
    
    Define los diferentes roles que pueden ser asignados a los usuarios
    para controlar permisos y acceso a recursos.

    Autor: Jeronimo Rodriguez (10/30/2025)
    """
    
    ROLES_DISPONIBLES = [
        ('administrador', 'Administrador'),
        ('veterinario', 'Veterinario'),
        ('practicante', 'Practicante'),
        ('recepcionista', 'Recepcionista'),
        ('cliente', 'Cliente'),
    ]
    
    nombre = models.CharField(
        'Nombre del rol',
        max_length=50,
        choices=ROLES_DISPONIBLES,
        unique=True
    )
    descripcion = models.TextField('Descripción', blank=True)
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']
    
    def __str__(self):
        return self.get_nombre_display()


class UsuarioRol(models.Model):
    """
    Tabla intermedia para la relación muchos a muchos entre Usuario y Rol.
    
    Permite que un usuario tenga múltiples roles y un rol pueda ser asignado
    a múltiples usuarios.

    Autor: Jeronimo Rodriguez (10/30/2025)
    """
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='usuario_roles'
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        related_name='rol_usuarios'
    )
    
    class Meta:
        db_table = 'usuario_roles'
        verbose_name = 'Usuario-Rol'
        verbose_name_plural = 'Usuarios-Roles'
        unique_together = ['usuario', 'rol']
        ordering = ['usuario', 'rol']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.rol.nombre}"
