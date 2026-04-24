from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from inventario.models import Kardex
from inventario.serializers import KardexSerializer
from inventario.services import KardexService
from inventario.permissions import IsAdminOrRecepcionista


class KardexViewSet(viewsets.ModelViewSet):

    serializer_class = KardexSerializer
    queryset = Kardex.objects.all().order_by('-fecha')
    permission_classes = [IsAuthenticated, IsAdminOrRecepcionista]

    def get_queryset(self):

        buscador = self.request.query_params.get("buscador")
        if buscador:
            return Kardex.objects.filter(
                Q(producto__nombre__icontains=buscador) |
                Q(detalle__icontains=buscador)
            ).order_by('-fecha')
        return Kardex.objects.all().order_by('-fecha')

    def destroy(self, request, *args, **kwargs):
        kardex = self.get_object()

        # Si ya está anulado → no permitir eliminar
        if kardex.detalle and "ANULADO" in kardex.detalle:
            raise ValidationError("No se puede eliminar un movimiento ANULADO.")

        # Si no está anulado → anularlo en lugar de eliminar
        service = KardexService()
        service.anular_movimiento(kardex, usuario=request.user)
        return Response({"detail": "Movimiento anulado correctamente."}, status=200)