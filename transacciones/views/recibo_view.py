"""
Vista para generar recibos de facturas.
Proporciona datos estructurados para impresión o generación de PDF.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from transacciones.models.factura import Factura
from transacciones.models.pago import Pago
from django.shortcuts import get_object_or_404


def _obtener_rol_usuario(usuario):
    """
    Obtiene el primer rol asociado al usuario.
    
    Args:
        usuario: Instancia de Usuario
        
    Returns:
        str: nombre del rol o None si no tiene rol asignado
    """
    usuario_rol = usuario.usuario_roles.first()
    if usuario_rol:
        return usuario_rol.rol.nombre
    return None


class ReciboFacturaView(APIView):
    """
    Endpoint para obtener los datos de un recibo de factura.
    
    GET /api/v1/transacciones/facturas/<factura_id>/recibo/
    
    Retorna un JSON estructurado con todos los datos necesarios
    para generar un recibo (PDF, impresión, etc.).
    
    Permisos:
    - Administradores, veterinarios y recepcionistas: pueden ver cualquier recibo
    - Clientes: solo pueden ver sus propios recibos
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, factura_id):
        """
        Retorna los datos estructurados del recibo de factura.
        """
        try:
            # Obtener factura con todas las relaciones optimizadas
            factura = get_object_or_404(
                Factura.objects.select_related(
                    'cliente', 'cita', 'consulta'
                ).prefetch_related(
                    'detalles__producto',
                    'detalles__servicio',
                    'pagos__metodo'
                ),
                id=factura_id
            )
            
            # Verificar permisos
            usuario = request.user
            rol = _obtener_rol_usuario(usuario)
            roles_acceso_total = ['administrador', 'veterinario', 'recepcionista']
            
            # Si es cliente, solo puede ver sus propios recibos
            if rol == 'cliente' and factura.cliente != usuario:
                return Response(
                    {'error': 'No tienes permiso para ver este recibo.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Si no tiene rol válido, denegar acceso
            if rol not in roles_acceso_total and rol != 'cliente':
                return Response(
                    {'error': 'No tienes permiso para ver recibos.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Preparar datos del recibo
            recibo_data = {
                'factura_id': factura.id,
                'numero_factura': f"FAC-{factura.id:06d}",
                'fecha_emision': factura.fecha.isoformat(),
                'estado': factura.estado,
                'cliente': {
                    'id': factura.cliente.id,
                    'nombre_completo': factura.cliente.get_full_name() or factura.cliente.username,
                    'email': factura.cliente.email,
                    'username': factura.cliente.username,
                },
                'detalles': [
                    {
                        'id': detalle.id,
                        'descripcion': detalle.descripcion,
                        'producto_id': detalle.producto.id if detalle.producto else None,
                        'producto_nombre': detalle.producto.nombre if detalle.producto else None,
                        'servicio_id': detalle.servicio.id if detalle.servicio else None,
                        'servicio_nombre': detalle.servicio.nombre if detalle.servicio else None,
                        'cantidad': detalle.cantidad,
                        'precio_unitario': float(detalle.precio_unitario),
                        'subtotal': float(detalle.subtotal),
                    }
                    for detalle in factura.detalles.all()
                ],
                'totales': {
                    'subtotal': float(factura.subtotal),
                    'impuestos': float(factura.impuestos),
                    'total': float(factura.total),
                },
                'pagos': [
                    {
                        'id': pago.id,
                        'metodo_id': pago.metodo.id if pago.metodo else None,
                        'metodo_nombre': pago.metodo.nombre if pago.metodo else 'N/A',
                        'monto': float(pago.monto),
                        'fecha': pago.fecha.isoformat(),
                        'aprobado': pago.aprobado,
                        'referencia': pago.referencia or '',
                    }
                    for pago in factura.pagos.all()
                ],
                'total_pagado': float(sum(pago.monto for pago in factura.pagos.all())),
                'saldo_pendiente': float(factura.total - sum(pago.monto for pago in factura.pagos.all())),
                'vinculos': {
                    'cita_id': factura.cita.id if factura.cita else None,
                    'consulta_id': factura.consulta.id if factura.consulta else None,
                }
            }
            
            return Response(recibo_data, status=status.HTTP_200_OK)
            
        except Factura.DoesNotExist:
            return Response(
                {'error': 'Factura no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Error al generar el recibo',
                    'detalle': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

