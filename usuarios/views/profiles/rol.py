from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from usuarios.models import Usuario, Rol
from usuarios.serializers.crud import UsuarioListSerializer
from usuarios.serializers.profiles import RolSerializer


class RolViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para gestionar la información de roles del sistema.
    
    Este ViewSet proporciona endpoints para consultar los roles disponibles
    y los usuarios asignados a cada rol. No permite modificaciones ya que
    los roles son predefinidos en el sistema.

    Endpoints disponibles:
    - GET /roles/: Lista todos los roles del sistema
    - GET /roles/{id}/: Obtiene detalles de un rol específico
    - GET /roles/{id}/usuarios/: Lista usuarios que tienen el rol especificado

    Notas de implementación:
    - Hereda de ReadOnlyModelViewSet para garantizar solo operaciones de lectura
    - Utiliza autenticación pero no requiere roles específicos para consultar
    - Los resultados de usuarios por rol excluyen usuarios eliminados (soft-deleted)
    """
    
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def usuarios(self, request, pk=None):
        """Lista los usuarios que tienen este rol."""
        rol = self.get_object()
        usuarios = Usuario.objects.filter(
            usuario_roles__rol=rol,
            deleted_at__isnull=True
        )
        
        serializer = UsuarioListSerializer(usuarios, many=True)
        return Response(serializer.data)
