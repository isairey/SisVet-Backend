"""
view y endpoinds para gestionar Consultas Veterinarias.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from consultas.models import Consulta
from consultas.signals import consulta_consentimiento_signal
from consultas.serializers.consulta_serializers import (
    ConsultaSerializer,
    ConsultaListSerializer,
    ConsultaDetailSerializer,
    ConsultaCreateSerializer,
    ConsultaUpdateSerializer
)
from consultas.services.consulta_service import (
    crear_consulta,
    obtener_datos_personales
)
from consultas.services.consentimiento_service import enviar_consentimiento
from consultas.services.consulta_estadisticas_service import (
    estadisticas_consultas
)

class ConsultaViewSet(viewsets.ModelViewSet):
    """
    gestión completa de consultas veterinarias.
    """
    queryset = Consulta.objects.all().select_related(
        'mascota',
        'veterinario'
    ).prefetch_related(
        'prescripciones',
        'examenes',
        'vacunas'
    )
    permission_classes = [IsAuthenticated]

    # Filtros y búsqueda
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['mascota', 'veterinario', 'fecha_consulta']
    search_fields = ['mascota__nombre', 'diagnostico', 'descripcion_consulta']
    ordering_fields = ['fecha_consulta', 'created_at']
    ordering = ['-fecha_consulta']

    def get_serializer_class(self):
        """
        Retorna el serializer apropiado según la acción.
        """
        if self.action == 'list':
            return ConsultaListSerializer
        elif self.action == 'retrieve':
            return ConsultaDetailSerializer
        elif self.action == 'create':
            return ConsultaCreateSerializer
        elif self.action in ['update', 'partial_update']:  # <--- Agregar esto
            return ConsultaUpdateSerializer

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
        Filtra las consultas según el rol del usuario.
        
        - Clientes: solo ven sus propias consultas
        - Veterinarios, Administradores y Recepcionistas: ven todas las consultas
        """
        user = self.request.user
        queryset = super().get_queryset()
        
        rol = self._obtener_rol_usuario(user)
        roles_acceso_total = ['administrador', 'veterinario', 'recepcionista']
        
        # Si es cliente, solo mostrar sus consultas
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

    def perform_create(self, serializer):
        user = self.request.user
        """
        Guarda la consulta asignando automáticamente el veterinario actual.
        """
        if hasattr(user, "perfil_veterinario") and user.perfil_veterinario is not None:
            serializer.save(veterinario=user.perfil_veterinario)
        else:
            raise ValidationError({"detail": "El usuario autenticado no tiene un perfil de veterinario asociado."})

    @action(detail=True, methods=['post'], url_path='enviar-consentimiento')
    def enviar_consentimiento_view(self, request, pk=None):
        consulta = self.get_object()

        enviar_consentimiento(consulta)
        return Response({"detail": "Solicitud enviada correctamente"}, status=200)

    @action(detail=False, methods=['get'], url_path='mascota/(?P<mascota_id>[^/.]+)')
    def por_mascota(self, request, mascota_id=None):
        """
        Retorna todas las consultas de una mascota específica.
        """
        # Usar get_queryset() que ya aplica los filtros por rol
        consultas = self.get_queryset().filter(mascota_id=mascota_id)
        
        # Si no hay consultas, puede ser que no tenga permisos o que no existan
        if not consultas.exists():
            return Response(
                {'detail': 'No se encontraron consultas para esta mascota o no tiene permisos para verlas'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ConsultaListSerializer(consultas, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='veterinario/(?P<veterinario_id>[^/.]+)')
    def por_veterinario(self, request, veterinario_id=None):
        """
        Retorna todas las consultas atendidas por un veterinario.
        """
        consultas = self.get_queryset().filter(veterinario_id=veterinario_id)
        serializer = ConsultaListSerializer(consultas, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def datos_personales(self, request, pk=None):
        consulta = self.get_object()
        datos = obtener_datos_personales(consulta)
        return Response(datos)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        data = estadisticas_consultas(self.get_queryset())
        return Response(data)

    @action(detail=False, methods=['get'], url_path='disponibles-para-facturar')
    def disponibles_para_facturar(self, request):
        """
        GET /api/v1/consultas/disponibles-para-facturar/
        
        Retorna solo las consultas que NO tienen factura asociada (o solo tienen facturas anuladas).
        Útil para mostrar opciones al crear facturas desde consultas.
        """
        from transacciones.models.factura import Factura
        
        # Obtener queryset base con filtros de rol
        queryset = self.get_queryset()
        
        # Obtener IDs de consultas que ya tienen factura (excluyendo anuladas)
        consultas_con_factura = Factura.objects.filter(
            consulta__isnull=False
        ).exclude(
            estado='ANULADA'
        ).values_list('consulta_id', flat=True)
        
        # Filtrar consultas que NO tienen factura asociada
        queryset = queryset.exclude(id__in=consultas_con_factura)
        
        # Ordenar por fecha más reciente
        queryset = queryset.order_by('-fecha_consulta')
        
        # Serializar y retornar
        serializer = ConsultaListSerializer(queryset, many=True, context={'request': request})
        return Response({
            "count": queryset.count(),
            "results": serializer.data
        }, status=status.HTTP_200_OK)