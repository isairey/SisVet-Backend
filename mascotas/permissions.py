from rest_framework.permissions import BasePermission
from usuarios.models import UsuarioRol


class MascotaListPermission(BasePermission):
    """
    Permiso personalizado para controlar el acceso a los recursos de mascotas.

    Roles permitidos:
        * administrador, veterinario, recepcionista, cliente.
    """

    message = "No tienes permisos para acceder a este recurso."
    roles_permitidos = {'administrador', 'veterinario', 'recepcionista', 'cliente'}
    roles_acceso_total = {'administrador', 'veterinario', 'recepcionista'}

    def _obtener_rol_usuario(self, usuario):
        if not usuario or not usuario.is_authenticated:
            return None

        rol_cache = getattr(usuario, '_mascotas_rol_cache', None)
        if rol_cache is not None:
            return rol_cache

        rol = UsuarioRol.objects.filter(usuario=usuario).values_list('rol__nombre', flat=True).first()
        usuario._mascotas_rol_cache = rol
        return rol

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        rol = self._obtener_rol_usuario(request.user)
        return rol in self.roles_permitidos

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        rol = self._obtener_rol_usuario(request.user)

        if rol in self.roles_acceso_total:
            return True

        if rol == 'cliente':
            cliente = getattr(obj, 'cliente', None)
            return cliente and cliente.usuario_id == request.user.id

        return False
