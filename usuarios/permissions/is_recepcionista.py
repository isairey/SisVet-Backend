from rest_framework import permissions


class IsRecepcionista(permissions.BasePermission):
    """Permiso para verificar si el usuario es recepcionista."""
    
    message = 'Solo los recepcionistas pueden realizar esta acción.'
    
    def has_permission(self, request, view):
        """Verifica si el usuario tiene rol de recepcionista."""
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.usuario_roles.filter(rol__nombre__iexact='recepcionista').exists()
