from usuarios.views.crud.viewset import UsuarioViewSet as UsuarioViewSetBase
from usuarios.views.crud.actions_auth import UsuarioAuthActionsMixin
from usuarios.views.crud.actions_admin import UsuarioAdminActionsMixin
from usuarios.views.crud.actions_search import UsuarioSearchActionsMixin


class UsuarioViewSet(
    UsuarioAuthActionsMixin,
    UsuarioAdminActionsMixin,
    UsuarioSearchActionsMixin,
    UsuarioViewSetBase
):
    """
    ViewSet completo para la gestión de usuarios.
    Combina todas las acciones: autenticación, administración y búsqueda.
    
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
    pass
