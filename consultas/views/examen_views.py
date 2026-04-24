"""
Views y endpoinds para gestionar Exámenes médicos.
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from consultas.models import Examen
from consultas.serializers.examen_serializers import ExamenSerializer, ExamenCreateSerializer

class ExamenViewSet(viewsets.ModelViewSet):
    """
    para gestión de exámenes médicos.
    """

    queryset = Examen.objects.all().select_related('consulta')
    serializer_class = ExamenSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Retorna el serializer apropiado"""
        if self.action == 'create':
            return ExamenCreateSerializer
        return ExamenSerializer

    def get_queryset(self):
        """Filtra exámenes según permisos del usuario"""
        user = self.request.user
        queryset = super().get_queryset()

        # Si es propietario, solo exámenes de sus mascotas
        if hasattr(user, 'perfil_cliente'):
            return queryset.filter(consulta__mascota__cliente=user.perfil_cliente)

        return queryset

    @action(detail=False, methods=['get'], url_path='consulta/(?P<consulta_id>[^/.]+)')
    def por_consulta(self, request, consulta_id=None):
        """
        Retorna todos los exámenes de una consulta.
        """
        examenes = self.get_queryset().filter(consulta_id=consulta_id)
        serializer = self.get_serializer(examenes, many=True)
        return Response(serializer.data)