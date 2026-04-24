from rest_framework import permissions


class CanManageUsers(permissions.BasePermission):
    """Permiso para administradores y recepcionistas que pueden gestionar usuarios."""
    
    message = 'No tienes permisos para gestionar usuarios.'
    
    def has_permission(self, request, view):
        """Verifica si puede gestionar usuarios."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Administradores tienen acceso completo
        is_admin = request.user.usuario_roles.filter(rol__nombre__iexact='administrador').exists()
        if is_admin:
            return True
        
        # Recepcionistas solo pueden crear clientes (POST)
        is_recep = request.user.usuario_roles.filter(rol__nombre__iexact='recepcionista').exists()
        if is_recep and request.method == 'POST':
            return True
        
        return False
