from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from usuarios.models import Usuario
from usuarios.serializers.crud import (
    UsuarioListSerializer,
    UsuarioDetailSerializer,
    UsuarioCreateSerializer,
    UsuarioUpdateSerializer,
)
from usuarios.permissions import (
    IsAdministrador,
    CanManageUsers,
    IsOwnerOrAdmin
)


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la gestión completa de usuarios del sistema veterinario.
    
    Este ViewSet proporciona endpoints para todas las operaciones CRUD sobre usuarios,
    incluyendo funcionalidades especiales como activación/suspensión de cuentas,
    cambio de contraseña y búsqueda avanzada.

    Endpoints principales:
    - GET /usuarios/: Lista todos los usuarios (requiere autenticación)
    - POST /usuarios/: Crea nuevo usuario (requiere ser admin o recepcionista)
    - GET /usuarios/{id}/: Detalle de usuario específico
    - PUT/PATCH /usuarios/{id}/: Actualización de usuario
    - DELETE /usuarios/{id}/: Eliminación lógica de usuario

    Endpoints especiales:
    - POST /usuarios/{id}/activar/: Activa un usuario
    - POST /usuarios/{id}/suspender/: Suspende un usuario
    - POST /usuarios/{id}/cambiar_password/: Cambio de contraseña
    - GET /usuarios/me/: Información del usuario actual
    - GET /usuarios/buscar/: Búsqueda avanzada
    - GET /usuarios/estadisticas/: Estadísticas de usuarios

    Permisos por operación:
    - Listado/Detalle: Cualquier usuario autenticado
    - Creación: Administradores y Recepcionistas (estos últimos solo pueden crear clientes)
    - Actualización: El propio usuario o un Administrador
    - Eliminación: Solo Administradores
    - Activar/Suspender: Solo Administradores
    
    Notas de implementación:
    - Utiliza soft delete para preservar histórico
    - Soporta filtrado por estado y rol
    - Incluye búsqueda por username, email y nombre
    - Optimizado con select_related para perfiles y prefetch_related para roles
    """
    
    queryset = Usuario.objects.filter(deleted_at__isnull=True).select_related(
        'perfil_veterinario',
        'perfil_practicante',
        'perfil_cliente'
    ).prefetch_related('usuario_roles__rol')
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'usuario_roles__rol__nombre']
    search_fields = ['username', 'email', 'nombre', 'apellido']
    ordering_fields = ['created_at', 'nombre', 'apellido']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == 'list':
            return UsuarioListSerializer
        elif self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UsuarioUpdateSerializer
        return UsuarioDetailSerializer
    
    def get_permissions(self):
        """
        Define los permisos requeridos según la acción solicitada.

        Este método implementa una lógica de dos niveles para determinar permisos:
        1. Primero verifica si la acción tiene permisos específicos definidos
           via decorador @action(permission_classes=[...])
        2. Si no hay permisos específicos, aplica el mapeo predeterminado
           basado en el tipo de acción CRUD

        Returns:
            list: Lista de instancias de clases de permisos aplicables

        Notas de implementación:
        - Las acciones decoradas con @action tienen prioridad
        - Todas las acciones requieren autenticación base
        - Los permisos se acumulan (todos deben pasar)
        """
        # Si la acción tiene permisos definidos por el decorador @action,
        # respetarlos primero. El decorador añade el atributo
        # `permission_classes` al método correspondiente.
        action_name = getattr(self, 'action', None)
        if action_name:
            # El decorador @action añade `permission_classes` a la función
            # definida en la clase (la función no enlazada). Cuando se obtiene
            # el atributo desde la instancia se obtiene un método enlazado y
            # puede que la metadata no sea visible directamente. Por eso
            # comprobamos primero en la función del atributo de la clase.
            action_func = getattr(self.__class__, action_name, None)
            if action_func is not None and hasattr(action_func, 'permission_classes'):
                return [perm() for perm in getattr(action_func, 'permission_classes')]

        # Mapeo por acción por defecto (para las acciones CRUD principales)
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated, CanManageUsers]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsAdministrador]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
    
    def perform_destroy(self, instance):
        """Implementa eliminación lógica (soft delete)."""
        instance.soft_delete()
