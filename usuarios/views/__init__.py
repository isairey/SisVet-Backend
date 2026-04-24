from usuarios.views.auth import (
    CustomTokenObtainPairView,
    RegistroView,
    PerfilView,
    cambiar_password_view,
    logout_view,
    verificar_token_view,
    ResetPasswordRequestView,
    ResetPasswordConfirmView,
    RegistroUsuarioAPIView,
    VerificarCodigoAPIView,
    ReenviarCodigoAPIView
)
from usuarios.views.crud import UsuarioViewSet
from usuarios.views.profiles import RolViewSet

__all__ = [
    # Auth views
    'CustomTokenObtainPairView',
    'RegistroView',
    'PerfilView',
    'cambiar_password_view',
    'logout_view',
    'verificar_token_view',
    'ResetPasswordRequestView',
    'ResetPasswordConfirmView',
    # CRUD views
    'UsuarioViewSet',
    # Profiles views
    'RolViewSet',
    # Registro dos pasos 
    'RegistroUsuarioAPIView',
    'VerificarCodigoAPIView',
    'ReenviarCodigoAPIView'
]
