"""
Vista para reportes financieros del sistema.
Proporciona estadísticas y análisis de facturas y pagos.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from transacciones.models.factura import Factura
from transacciones.permissions import IsAdminVeterinarioOrRecepcionista


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


class ReportesFinancierosView(APIView):
    """
    Endpoint para obtener reportes y estadísticas financieras.
    
    Solo accesible para administradores, veterinarios y recepcionistas.
    
    GET /api/v1/transacciones/reportes-financieros/
    
    Retorna:
    - Resumen general (total facturas, pagadas, pendientes, ingresos)
    - Ingresos del mes actual
    - Estadísticas por estado
    """
    permission_classes = [IsAuthenticated, IsAdminVeterinarioOrRecepcionista]

    def get(self, request):
        """
        Genera y retorna el reporte financiero completo.
        """
        try:
            # Obtener queryset base
            facturas = Factura.objects.all()
            
            # Estadísticas generales
            total_facturas = facturas.count()
            facturas_pagadas = facturas.filter(estado='PAGADA').count()
            facturas_pendientes = facturas.filter(estado='PENDIENTE').count()
            facturas_anuladas = facturas.filter(estado='ANULADA').count()
            
            # Ingresos totales (solo facturas pagadas)
            ingresos_totales = facturas.filter(
                estado='PAGADA'
            ).aggregate(total=Sum('total'))['total'] or 0
            
            # Ingresos del mes actual
            mes_actual = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            ingresos_mes = facturas.filter(
                estado='PAGADA',
                fecha__gte=mes_actual
            ).aggregate(total=Sum('total'))['total'] or 0
            
            # Ingresos de la semana actual
            semana_actual = timezone.now() - timedelta(days=7)
            ingresos_semana = facturas.filter(
                estado='PAGADA',
                fecha__gte=semana_actual
            ).aggregate(total=Sum('total'))['total'] or 0
            
            # Facturas por estado con totales
            por_estado = facturas.values('estado').annotate(
                cantidad=Count('id'),
                total=Sum('total')
            ).order_by('estado')
            
            # Facturas del mes actual por estado
            facturas_mes = facturas.filter(fecha__gte=mes_actual)
            por_estado_mes = facturas_mes.values('estado').annotate(
                cantidad=Count('id'),
                total=Sum('total')
            ).order_by('estado')
            
            # Promedio de factura
            promedio_factura = 0
            if total_facturas > 0:
                promedio_factura = float(ingresos_totales) / total_facturas
            
            return Response({
                'resumen': {
                    'total_facturas': total_facturas,
                    'facturas_pagadas': facturas_pagadas,
                    'facturas_pendientes': facturas_pendientes,
                    'facturas_anuladas': facturas_anuladas,
                    'ingresos_totales': float(ingresos_totales),
                    'ingresos_mes_actual': float(ingresos_mes),
                    'ingresos_semana_actual': float(ingresos_semana),
                    'promedio_factura': round(promedio_factura, 2),
                },
                'por_estado': [
                    {
                        'estado': item['estado'],
                        'cantidad': item['cantidad'],
                        'total': float(item['total'] or 0)
                    }
                    for item in por_estado
                ],
                'por_estado_mes_actual': [
                    {
                        'estado': item['estado'],
                        'cantidad': item['cantidad'],
                        'total': float(item['total'] or 0)
                    }
                    for item in por_estado_mes
                ],
                'periodo': {
                    'mes_actual': mes_actual.strftime('%Y-%m'),
                    'fecha_consulta': timezone.now().isoformat()
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {
                    'error': 'Error al generar el reporte financiero',
                    'detalle': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

