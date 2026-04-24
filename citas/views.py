from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from citas.models import Cita, Servicio
from citas import serializers
from citas.services import cita_service 
from citas.services.disponibilidad_service import DisponibilidadService
_disponibilidad_service = DisponibilidadService()


class CitaViewSet(viewsets.ModelViewSet):
    """
    API Endpoint para Citas.
    Refactorizado para delegar lógica a Servicios y Patrones (Command & Composite).
    """
    queryset = Cita.objects.all().select_related('mascota', 'veterinario', 'servicio')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Selecciona el serializer adecuado.
        Nota: Los serializers de escritura (Crear/Reagendar) SOLO VALIDAN.
        """
        if self.action == 'create':
            return serializers.CrearCitaSerializer
        if self.action == 'reagendar':
            return serializers.ReagendarCitaSerializer
        return serializers.CitaSerializer

    def get_queryset(self):
        """
        Filtra citas por rol.
        """
        user = self.request.user
        if hasattr(user, 'usuario_roles'):
            roles = [r.rol.nombre for r in user.usuario_roles.all()]
            if 'cliente' in roles:
                return self.queryset.filter(mascota__cliente__usuario=user)
            if 'veterinario' in roles:
                return self.queryset.filter(veterinario=user)
        return self.queryset.all()

    # --- ACCIONES DE ESCRITURA (USANDO PATRÓN COMMAND) ---

    def create(self, request, *args, **kwargs):
        """
        POST /api/v1/citas/
        Agendar una nueva cita.
        """
        # 1. Validación de Datos (Serializer)
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # 2. Lógica de Negocio (Servicio -> Command)
        try:
            # Pasamos los datos validados al servicio
            cita_creada = cita_service.ejecutar_agendamiento(
                data=serializer.validated_data, 
                usuario=request.user
            )
            
            # 3. Respuesta (Serializer de Lectura)
            read_serializer = serializers.CitaSerializer(cita_creada)
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Captura errores de negocio (ej: horario ocupado, mascota no existe)
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='cancelar')
    def cancelar(self, request, pk=None):
        """
        POST /api/v1/citas/{id}/cancelar/
        Cancelar una cita existente.
        """
        try:
            # Delegamos al servicio
            cita = cita_service.ejecutar_cancelacion(pk, request.user)
            return Response(serializers.CitaSerializer(cita).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='reagendar')
    def reagendar(self, request, pk=None):
        """
        POST /api/v1/citas/{id}/reagendar/
        Cambiar la fecha de una cita.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Extraemos la fecha validada
            nueva_fecha = serializer.validated_data['fecha_hora'].isoformat()
            
            # Delegamos al servicio
            cita = cita_service.ejecutar_reagendamiento(pk, nueva_fecha, request.user)
            
            return Response(serializers.CitaSerializer(cita).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # --- ACCIONES DE LECTURA (USANDO PATRÓN COMPOSITE) ---

    @action(detail=False, methods=['get'], url_path='disponibilidad')
    def disponibilidad(self, request):
        """
        GET /api/v1/citas/disponibilidad/?veterinario_id=X&fecha=YYYY-MM-DD
        """
        veterinario_id = request.query_params.get('veterinario_id')
        fecha_str = request.query_params.get('fecha')

        if not veterinario_id or not fecha_str:
            return Response({"error": "Faltan parámetros (veterinario_id, fecha)"}, status=400)

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            # Delegamos al servicio que usa el Composite
            horarios = _disponibilidad_service.calcular_horarios_disponibles(veterinario_id, fecha)
            return Response({"horarios_disponibles": horarios}, status=200)
        except ValueError:
            return Response({"error": "Formato de fecha inválido"}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=False, methods=['get'], url_path='disponibles-para-facturar')
    def disponibles_para_facturar(self, request):
        """
        GET /api/v1/citas/disponibles-para-facturar/
        
        Retorna solo las citas que NO tienen factura asociada (o solo tienen facturas anuladas).
        Útil para mostrar opciones al crear facturas desde citas.
        """
        from transacciones.models.factura import Factura
        
        # Obtener queryset base con filtros de rol
        queryset = self.get_queryset()
        
        # Obtener IDs de citas que ya tienen factura (excluyendo anuladas)
        citas_con_factura = Factura.objects.filter(
            cita__isnull=False
        ).exclude(
            estado='ANULADA'
        ).values_list('cita_id', flat=True)
        
        # Filtrar citas que NO tienen factura asociada
        queryset = queryset.exclude(id__in=citas_con_factura)
        
        # Filtrar solo citas que tienen servicio (necesario para crear factura)
        queryset = queryset.filter(servicio__isnull=False)
        
        # Ordenar por fecha más reciente
        queryset = queryset.order_by('-fecha_hora')
        
        # Serializar y retornar
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "count": queryset.count(),
            "results": serializer.data
        }, status=status.HTTP_200_OK)


class ServicioViewSet(viewsets.ModelViewSet):
    """
    CRUD simple para Servicios.
    """
    queryset = Servicio.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers.ServicioWriteSerializer
        return serializers.ServicioSerializer