"""
Permisos personalizados para el módulo de transacciones.
"""
from rest_framework import permissions


class IsAdminVeterinarioOrRecepcionista(permissions.BasePermission):
    """
    Permiso que verifica si el usuario tiene alguno de los roles:
    - administrador
    - veterinario
    - recepcionista
    
    Útil para endpoints que requieren acceso administrativo o del personal.
    """
    message = 'Solo administradores, veterinarios o recepcionistas pueden realizar esta acción.'

    def has_permission(self, request, view):
        """Verifica si el usuario tiene alguno de los roles permitidos."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Verificar si tiene alguno de los roles permitidos
        roles_permitidos = ['administrador', 'veterinario', 'recepcionista']
        return request.user.usuario_roles.filter(
            rol__nombre__in=roles_permitidos
        ).exists()

