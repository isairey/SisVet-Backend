from rest_framework import permissions


class HasRolePermission(permissions.BasePermission):
    """
    Permiso configurable que verifica si un usuario tiene al menos uno
    de los roles especificados.

    Este permiso es flexible y puede utilizarse para proteger endpoints
    que requieren roles específicos o combinaciones de roles.

    Args:
        allowed_roles (list): Lista de nombres de roles permitidos.
                            Los nombres son case-insensitive.

    Ejemplo de uso:
        @action(
            detail=True,
            permission_classes=[IsAuthenticated, HasRolePermission(['veterinario', 'practicante'])]
        )
        def atender_mascota(self, request, pk=None):
            ...

    Notas de implementación:
        - Los nombres de roles se normalizan a minúsculas para comparación
        - La validación es case-insensitive para mayor robustez
        - Si el usuario tiene múltiples roles, basta con que uno coincida
    """
    message = 'No tienes el rol requerido para realizar esta acción.'

    def __init__(self, allowed_roles):
        """
        Args:
            allowed_roles: Lista de roles permitidos
        """
        self.allowed_roles = allowed_roles
        super().__init__()
    
    def has_permission(self, request, view):
        """Verifica si el usuario tiene alguno de los roles permitidos."""
        if not request.user or not request.user.is_authenticated:
            return False
        # Retorna True si el usuario tiene alguno de los roles en allowed_roles
        # Hacemos comparación case-insensitive para mayor robustez:
        allowed_normalized = [r.lower() for r in self.allowed_roles]
        return request.user.usuario_roles.filter(rol__nombre__in=allowed_normalized).exists()
