from rest_framework import permissions

# Jerónimo Rodríguez - 06/11/2025
class IsAdministrador(permissions.BasePermission):
    """
    Permiso que verifica si el usuario tiene el rol de administrador.

    Este permiso se usa para proteger acciones que solo deben ser accesibles
    para administradores del sistema, como la gestión de usuarios, activación
    y suspensión de cuentas.

    Ejemplos de uso:
        @action(detail=True, permission_classes=[IsAuthenticated, IsAdministrador])
        def activar(self, request, pk=None):
            ...

    Comportamiento:
        - Requiere que el usuario esté autenticado
        - Realiza una búsqueda case-insensitive del rol 'administrador'
        - Retorna False si el usuario no está autenticado o no tiene el rol
    """

    message = 'Solo los administradores pueden realizar esta acción.'

    def has_permission(self, request, view):
        """Verifica si el usuario tiene rol de administrador."""
        if not request.user or not request.user.is_authenticated:
            return False
        # Comprobar que el usuario tenga el rol 'administrador' (case-insensitive)
        return request.user.usuario_roles.filter(rol__nombre__iexact='administrador').exists()
