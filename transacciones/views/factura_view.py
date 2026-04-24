from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from transacciones.models.factura import Factura
from transacciones.serializers.factura_serializer import FacturaSerializer


def _obtener_rol_usuario(usuario):
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


class FacturaListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear facturas.
    
    - GET: Lista facturas con filtros, búsqueda y ordenamiento
    - POST: Crea una nueva factura asociada al usuario autenticado
    
    Filtros disponibles:
    - estado: PENDIENTE, PAGADA, ANULADA
    - cliente: ID del cliente
    - pagada: true/false
    
    Búsqueda:
    - Por ID de factura, nombre, apellido o email del cliente
    
    Ordenamiento:
    - Por fecha, total o ID (ascendente o descendente)
    """
    serializer_class = FacturaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'cliente', 'pagada']
    search_fields = ['id', 'cliente__nombre', 'cliente__apellido', 'cliente__email']
    ordering_fields = ['fecha', 'total', 'id']
    ordering = ['-fecha']  # Por defecto, más recientes primero

    def get_queryset(self):
        """
        Retorna el queryset de facturas según el rol del usuario.
        
        - Administradores, veterinarios y recepcionistas: ven todas las facturas
        - Clientes: solo ven sus propias facturas
        """
        queryset = Factura.objects.all().select_related(
            'cliente', 'cita', 'consulta'
        ).prefetch_related(
            'detalles__producto',
            'detalles__servicio',
            'pagos__metodo'
        )
        
        usuario = self.request.user
        if not usuario.is_authenticated:
            return Factura.objects.none()
        
        rol = _obtener_rol_usuario(usuario)
        roles_acceso_total = ['administrador', 'veterinario', 'recepcionista']
        
        # Si es cliente, solo mostrar sus facturas
        if rol == 'cliente':
            queryset = queryset.filter(cliente=usuario)
        elif rol not in roles_acceso_total:
            # Si no tiene rol válido, no mostrar nada (seguridad por defecto)
            queryset = Factura.objects.none()
        
        return queryset

    def perform_create(self, serializer):
        """Asigna el cliente autenticado a la factura."""
        serializer.save(cliente=self.request.user)


class FacturaDetailView(generics.RetrieveAPIView):
    """
    Vista para obtener el detalle de una factura específica.
    
    - GET: Retorna la factura con todos sus detalles y pagos
    """
    serializer_class = FacturaSerializer

    def get_queryset(self):
        """
        Retorna el queryset de facturas según el rol del usuario.
        
        - Administradores, veterinarios y recepcionistas: pueden ver cualquier factura
        - Clientes: solo pueden ver sus propias facturas
        """
        queryset = Factura.objects.all().select_related(
            'cliente', 'cita', 'consulta'
        ).prefetch_related(
            'detalles__producto',
            'detalles__servicio',
            'pagos__metodo'
        )
        
        usuario = self.request.user
        if not usuario.is_authenticated:
            return Factura.objects.none()
        
        rol = _obtener_rol_usuario(usuario)
        roles_acceso_total = ['administrador', 'veterinario', 'recepcionista']
        
        # Si es cliente, solo mostrar sus facturas
        if rol == 'cliente':
            queryset = queryset.filter(cliente=usuario)
        elif rol not in roles_acceso_total:
            # Si no tiene rol válido, no mostrar nada (seguridad por defecto)
            queryset = Factura.objects.none()
        
        return queryset