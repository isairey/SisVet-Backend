from rest_framework import permissions
from usuarios.models import UsuarioRol


class IsAdminOrRecepcionista(permissions.BasePermission):
    """
    Permiso que permite acceso solo a administradores y recepcionistas.
    Excluye explícitamente a veterinarios.
    
    Roles permitidos:
    - administrador
    - recepcionista
    """
    message = 'Solo administradores o recepcionistas pueden acceder al módulo de inventario.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True

        roles = UsuarioRol.objects.filter(usuario=request.user).values_list('rol__nombre', flat=True)
        roles_permitidos = ['administrador', 'recepcionista']
        return any(rol in roles_permitidos for rol in roles)

