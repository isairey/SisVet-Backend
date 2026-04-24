from rest_framework import permissions


class IsCliente(permissions.BasePermission):
    """Permiso para verificar si el usuario es cliente."""
    
    message = 'Solo los clientes pueden realizar esta acción.'
    
    def has_permission(self, request, view):
        """Verifica si el usuario tiene rol de cliente."""
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.usuario_roles.filter(rol__nombre__iexact='cliente').exists()
