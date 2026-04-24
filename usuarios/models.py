"""
11/16/2025
DEPRECADO: Este archivo ha sido refactorizado.

Todos los modelos han sido movidos a la carpeta `models/` con una estructura modular:
  - models/auth/usuario.py -> Usuario, UsuarioPendiente
  - models/auth/rol.py -> Rol, UsuarioRol
  - models/profiles/ -> Veterinario, Practicante, Cliente
  - models/auth/reset_password_token.py -> ResetPasswordToken

Para mantener compatibilidad, los imports se redirigen automaticamente.
"""

# Re-exportar todos los modelos desde la nueva estructura
from usuarios.models.auth.usuario import Usuario
from usuarios.models.auth.usuario_pendiente import UsuarioPendiente
from usuarios.models.auth.rol import Rol, UsuarioRol
from usuarios.models.profiles import Veterinario, Practicante, Cliente
from usuarios.models.auth.reset_password_token import ResetPasswordToken

__all__ = [
    "Usuario",
    "UsuarioPendiente",
    "Rol",
    "UsuarioRol",
    "Veterinario",
    "Practicante",
    "Cliente",
    "ResetPasswordToken",
]
