from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError

from transacciones.services.factura_service import FacturaService
from transacciones.serializers.factura_serializer import FacturaSerializer
from transacciones.serializers.factura_producto_serializer import CrearFacturaDesdeProductosSerializer
from usuarios.models import UsuarioRol


def _obtener_rol_usuario(usuario):
    """
    Obtiene el primer rol asociado al usuario.
    """
    usuario_rol = usuario.usuario_roles.first()
    if usuario_rol:
        return usuario_rol.rol.nombre
    return None


class CrearFacturaDesdeProductosView(APIView):
    """
    Vista para crear una factura desde productos (venta directa desde inventario).
    
    Permite crear facturas directamente desde productos sin necesidad de cita o consulta.
    Registra automáticamente los movimientos en el inventario (Kardex).
    
    Requiere autenticación y permisos de administrador, veterinario o recepcionista.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Crea una factura desde productos.
        
        Body esperado:
        {
            "cliente_id": 1,
            "productos": [
                {"producto_id": 1, "cantidad": 2},
                {"producto_id": 3, "cantidad": 1}
            ]
        }
        """
        # Validar permisos
        usuario = request.user
        rol = _obtener_rol_usuario(usuario)
        roles_permitidos = ['administrador', 'veterinario', 'recepcionista']

        if not usuario.is_superuser and rol not in roles_permitidos:
            return Response(
                {
                    "error": "No tienes permisos para crear facturas desde productos. "
                             "Solo administradores, veterinarios y recepcionistas pueden realizar esta operación."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Validar datos con serializer
        serializer = CrearFacturaDesdeProductosSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        cliente_id = serializer.validated_data['cliente_id']
        productos_data = serializer.validated_data['productos']

        try:
            # Crear factura desde productos
            factura = FacturaService.crear_factura_desde_productos(
                cliente_id=cliente_id,
                productos_data=productos_data,
                usuario=usuario
            )

            # Retornar factura serializada
            factura_serializer = FacturaSerializer(factura)
            return Response(
                {
                    "mensaje": "Factura creada exitosamente desde productos.",
                    "factura": factura_serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Error al crear la factura: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

