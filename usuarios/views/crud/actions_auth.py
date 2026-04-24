from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from usuarios.serializers.crud import CambiarPasswordSerializer
from usuarios.permissions import IsOwnerOrAdmin


class UsuarioAuthActionsMixin:
    """
    Mixin que proporciona acciones de autenticación y gestión de contraseñas
    para el UsuarioViewSet.
    """
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOwnerOrAdmin])
    def cambiar_password(self, request, pk=None):
        """
        Permite al usuario cambiar su contraseña.
        
        Solo el propietario del usuario o un administrador pueden cambiar la contraseña.
        El permiso IsOwnerOrAdmin se verifica automáticamente por DRF en get_object().
        
        Nota: El serializer valida password_actual contra request.user:
        - Si el usuario cambia su propia contraseña: debe proporcionar su propia contraseña actual
        - Si un administrador cambia la contraseña de otro usuario: debe proporcionar su propia contraseña (del admin)
        
        Verificamos permisos explícitamente antes de validar el serializer para asegurar
        que se devuelva 403 (FORBIDDEN) en lugar de 400 (BAD REQUEST) cuando el usuario
        no tiene permisos para cambiar la contraseña de otro usuario.
        """
        usuario = self.get_object()  # Obtiene el usuario objetivo
        
        # Verificar permisos explícitamente antes de validar el serializer
        # Esto asegura que se devuelva 403 en lugar de 400 cuando no hay permisos
        permiso = IsOwnerOrAdmin()
        if not permiso.has_object_permission(request, self, usuario):
            raise PermissionDenied(
                detail='No tienes permisos para cambiar la contraseña de este usuario.'
            )
        
        serializer = CambiarPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # Cambiar la contraseña del usuario objetivo
            usuario.set_password(serializer.validated_data['password_nueva'])
            usuario.save()
            
            return Response(
                {'detail': 'Contraseña actualizada correctamente.'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
