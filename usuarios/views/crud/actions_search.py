from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from usuarios.serializers.crud import UsuarioListSerializer
from usuarios.serializers.profiles import RolSerializer
from usuarios.serializers.crud import UsuarioDetailSerializer


class UsuarioSearchActionsMixin:
    """
    Mixin que proporciona acciones de búsqueda y recuperación de datos
    para el UsuarioViewSet. Incluye: me y buscar.
    """
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Retorna la información del usuario autenticado."""
        serializer = UsuarioDetailSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def buscar(self, request):
        """
        Realiza una búsqueda avanzada de usuarios con múltiples criterios.
        
        Este endpoint permite buscar usuarios combinando varios criterios:
        - Texto libre (busca en username, email, nombre, apellido)
        - Filtrado por rol específico
        - Filtrado por estado del usuario
        
        Parámetros de query:
        - q (str): Texto a buscar en campos de usuario
        - rol (str): Nombre del rol para filtrar
        - estado (str): Estado del usuario (default: 'activo')
        
        Características:
        - Búsqueda case-insensitive en todos los campos
        - Soporte para paginación de resultados
        - Excluye usuarios eliminados (soft-deleted)
        
        Returns:
            Response: Lista paginada de usuarios que coinciden con los criterios,
                     serializados con UsuarioListSerializer
        """
        query = request.query_params.get('q', '')
        rol = request.query_params.get('rol', None)
        estado = request.query_params.get('estado', 'activo')
        
        usuarios = self.queryset.filter(estado=estado)
        
        if query:
            usuarios = usuarios.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(nombre__icontains=query) |
                Q(apellido__icontains=query)
            )
        
        if rol:
            usuarios = usuarios.filter(usuario_roles__rol__nombre=rol)
        
        # Paginar resultados
        page = self.paginate_queryset(usuarios)
        if page is not None:
            serializer = UsuarioListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UsuarioListSerializer(usuarios, many=True)
        return Response(serializer.data)
