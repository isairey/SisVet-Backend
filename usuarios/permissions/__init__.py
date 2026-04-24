from usuarios.permissions.is_administrador import IsAdministrador
from usuarios.permissions.is_owner_or_admin import IsOwnerOrAdmin
from usuarios.permissions.is_admin_or_readonly import IsAdminOrReadOnly
from usuarios.permissions.can_manage_users import CanManageUsers
from usuarios.permissions.has_role_permission import HasRolePermission
from usuarios.permissions.is_veterinario import IsVeterinario
from usuarios.permissions.is_recepcionista import IsRecepcionista
from usuarios.permissions.is_cliente import IsCliente

__all__ = [
    'IsAdministrador',
    'IsOwnerOrAdmin',
    'IsAdminOrReadOnly',
    'CanManageUsers',
    'HasRolePermission',
    'IsVeterinario',
    'IsRecepcionista',
    'IsCliente',
]
