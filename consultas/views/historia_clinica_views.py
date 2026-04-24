"""
view y endpoints para Historia Clínica Consolidada.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Count

from consultas.models import HistoriaClinica
from consultas.serializers.historia_clinica_serializers import (
    HistoriaClinicaSerializer,
    HistoriaClinicaDetalleSerializer,
    UltimaConsultaSerializer
)


class HistoriaClinicaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para visualizar historias clínicas consolidadas.
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['mascota']
    search_fields = [
        'mascota__nombre',
        'mascota__cliente__usuario__nombre',
        'mascota__cliente__usuario__apellido'
    ]

    def _obtener_rol_usuario(self, usuario):
        """
        Obtiene el primer rol asociado al usuario.
        
        Args:
            usuario: Instancia de Usuario
            
        Returns:
            str: nombre del rol (ej: 'administrador', 'veterinario', 'recepcionista', 'cliente')
                 o None si no tiene rol asignado
        """
        usuario_rol = usuario.usuario_roles.first()
        if usuario_rol:
            return usuario_rol.rol.nombre
        return None

    def get_queryset(self):
        """
        Filtra historias según el rol del usuario.
        
        - Clientes: solo ven las historias clínicas de sus propias mascotas
        - Veterinarios, Administradores y Recepcionistas: ven todas las historias clínicas
        """
        user = self.request.user

        queryset = HistoriaClinica.objects.select_related(
            'mascota',
            'mascota__cliente',
            'mascota__cliente__usuario',
            'mascota__especie',
            'mascota__raza'
        ).prefetch_related(
            'mascota__consultas'
        )

        rol = self._obtener_rol_usuario(user)
        roles_acceso_total = ['administrador', 'veterinario', 'recepcionista']
        
        # Si es cliente, solo mostrar historias de sus mascotas
        if rol == 'cliente':
            # Obtener el perfil_cliente del usuario
            if hasattr(user, 'perfil_cliente'):
                return queryset.filter(mascota__cliente__usuario=user)
            # Si no tiene perfil_cliente pero es cliente, no mostrar nada
            return queryset.none()

        # Si es veterinario, administrador o recepcionista, puede ver todas
        if rol in roles_acceso_total:
            return queryset
        
        # Por defecto, no mostrar nada (seguridad)
        return queryset.none()

    def get_serializer_class(self):
        """
        Retorna el serializer apropiado según la acción.
        """
        if self.action == 'retrieve' or self.action == 'por_mascota':
            return HistoriaClinicaDetalleSerializer
        elif self.action == 'ultima_consulta':
            return UltimaConsultaSerializer
        return HistoriaClinicaSerializer

    @action(detail=False, methods=['get'], url_path='mascota/(?P<mascota_id>[^/.]+)')
    def por_mascota(self, request, mascota_id=None):
        """
        Retorna la historia clínica de una mascota por su ID.
        """
        try:
            historia = self.get_queryset().get(mascota_id=mascota_id)
        except HistoriaClinica.DoesNotExist:
            return Response(
                {'detail': 'Esta mascota no tiene historia clínica registrada o no tienes permisos para verla'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(historia)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='ultima-consulta')
    def ultima_consulta(self, request, pk=None):
        """
        Retorna solo la última consulta de la historia clínica.
        """
        historia = self.get_object()
        serializer = UltimaConsultaSerializer(historia, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """
        Búsqueda avanzada de historias clínicas.
        """
        query = request.query_params.get('q', '')

        if not query:
            return Response(
                {'detail': 'Debe proporcionar un término de búsqueda'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Usar get_queryset() para respetar los permisos
        historias = self.get_queryset().filter(
            mascota__nombre__icontains=query
        ) | self.get_queryset().filter(
            mascota__cliente__usuario__nombre__icontains=query
        ) | self.get_queryset().filter(
            mascota__cliente__usuario__apellido__icontains=query
        )

        serializer = HistoriaClinicaSerializer(historias.distinct(), many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Retorna estadísticas generales de historias clínicas.
        Útil para el dashboard de veterinarios.
        """
        queryset = self.get_queryset()
        
        total_historias = queryset.count()
        
        return Response({
            'total_historias_clinicas': total_historias,
        })