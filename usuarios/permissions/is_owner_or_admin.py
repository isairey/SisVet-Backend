from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso que verifica si el usuario es el propietario del recurso o es administrador.

    Este permiso se utiliza para endpoints donde un usuario debe poder gestionar
    sus propios recursos, mientras que los administradores mantienen acceso
    completo a todos los recursos.

    Comportamiento:
        - Permite acceso si el usuario es administrador
        - Permite acceso si el usuario es el propietario del objeto
        - Deniega acceso en cualquier otro caso
    
    Nota: 
        Este permiso asume que el objeto tiene un ID que puede compararse
        con el ID del usuario autenticado.
    """
    
    message = 'Solo puedes editar tu propio perfil o ser administrador.'
    
    def has_object_permission(self, request, view, obj):
        """Verifica si el usuario es el dueño del objeto o administrador."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Si es administrador, tiene acceso total
        is_admin = request.user.usuario_roles.filter(rol__nombre__iexact='administrador').exists()
        if is_admin:
            return True
        
        # Si es el dueño del objeto
        if isinstance(obj, request.user.__class__):
            return obj.id == request.user.id
        
        return False
