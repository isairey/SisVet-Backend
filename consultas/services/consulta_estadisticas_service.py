# apps/consultas/services/consulta_estadisticas_service.py

from django.db.models import Count
from django.db.models.functions import TruncMonth

def estadisticas_consultas(queryset):
    """
    Devuelve estadísticas generales.
    """
    total = queryset.count()

    por_mes = queryset.annotate(
        mes=TruncMonth('fecha_consulta')
    ).values('mes').annotate(
        total=Count('id')
    ).order_by('-mes')[:6]

    return {
        'total_consultas': total,
        'consultas_por_mes': list(por_mes)
    }
