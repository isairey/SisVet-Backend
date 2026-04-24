from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permite lectura a todos pero escritura solo a administradores."""
    
    def has_permission(self, request, view):
        """Permite GET, HEAD, OPTIONS a todos; otros métodos solo a admins."""
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.usuario_roles.filter(
            rol__nombre__iexact='administrador'
        ).exists()
