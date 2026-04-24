from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db.models import Count, Q

from usuarios.models import Usuario, Rol
from usuarios.permissions import IsAdministrador


class UsuarioAdminActionsMixin:
    """
    Mixin que proporciona acciones administrativas para el UsuarioViewSet.
    Incluye: activación, suspensión y estadísticas de usuarios.
    """
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdministrador])
    def activar(self, request, pk=None):
        """
        Activa un usuario que se encuentra suspendido o inactivo.
        
        Este endpoint permite a los administradores reactivar cuentas de usuario
        que hayan sido suspendidas o desactivadas. Al activar un usuario:
        - Su estado cambia a 'activo'
        - Se establece is_active=True en su cuenta
        - Puede volver a iniciar sesión y acceder al sistema
        
        Permisos requeridos:
        - Usuario autenticado
        - Rol de administrador
        
        Returns:
            Response: Mensaje de éxito con estado HTTP 200
        """
        usuario = self.get_object()

        # Verificar permiso explícito por rol de administrador (defensa en profundidad)
        if not request.user.usuario_roles.filter(rol__nombre='administrador').exists():
            raise PermissionDenied(detail='No tienes permisos para activar usuarios.')

        usuario.estado = 'activo'
        usuario.is_active = True
        usuario.save()

        return Response(
            {'detail': f'Usuario {usuario.username} activado correctamente.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdministrador])
    def suspender(self, request, pk=None):
        """
        Suspende temporalmente un usuario activo del sistema.
        
        Este endpoint permite a los administradores suspender cuentas de usuario
        por motivos administrativos o de seguridad. Al suspender un usuario:
        - Su estado cambia a 'suspendido'
        - Se establece is_active=False en su cuenta
        - No podrá iniciar sesión hasta ser reactivado
        
        Validaciones:
        - No permite la auto-suspensión (un admin no puede suspender su propia cuenta)
        - Requiere permisos de administrador
        
        Permisos requeridos:
        - Usuario autenticado
        - Rol de administrador
        
        Returns:
            Response: Mensaje de éxito con estado HTTP 200 o error 400 si intenta
                     auto-suspenderse
        """
        usuario = self.get_object()

        # No permitir auto-suspensión
        if usuario.id == request.user.id:
            return Response(
                {'detail': 'No puedes suspender tu propia cuenta.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar permiso explícito por rol de administrador (defensa en profundidad)
        if not request.user.usuario_roles.filter(rol__nombre='administrador').exists():
            raise PermissionDenied(detail='No tienes permisos para suspender usuarios.')

        usuario.estado = 'suspendido'
        usuario.is_active = False
        usuario.save()

        return Response(
            {'detail': f'Usuario {usuario.username} suspendido correctamente.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def estadisticas(self, request):
        """
        Retorna estadísticas generales sobre los usuarios del sistema.
        
        Este endpoint proporciona un resumen estadístico que incluye:
        - Total de usuarios activos en el sistema
        - Total de usuarios por estado (activo/suspendido)
        - Distribución de usuarios por rol
        
        Las estadísticas excluyen usuarios eliminados (soft-deleted) y
        se calculan utilizando agregaciones de Django para eficiencia.
        
        Permisos:
        - Requiere autenticación
        - Acceso limitado a administradores
        
        Returns:
            Response: Diccionario con estadísticas agregadas:
                     - total_usuarios: int
                     - usuarios_activos: int
                     - usuarios_por_rol: dict[str, int]
        """
        if not request.user.usuario_roles.filter(rol__nombre='administrador').exists():
            return Response(
                {'detail': 'No tienes permisos para ver estadísticas.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = {
            'total_usuarios': Usuario.objects.filter(deleted_at__isnull=True).count(),
            'usuarios_activos': Usuario.objects.filter(
                estado='activo',
                deleted_at__isnull=True
            ).count(),
            'usuarios_por_rol': {}
        }
        
        # Contar usuarios por rol
        roles_count = Rol.objects.annotate(
            total=Count('rol_usuarios', filter=Q(
                rol_usuarios__usuario__deleted_at__isnull=True
            ))
        ).values('nombre', 'total')
        
        for rol in roles_count:
            stats['usuarios_por_rol'][rol['nombre']] = rol['total']
        
        return Response(stats)
