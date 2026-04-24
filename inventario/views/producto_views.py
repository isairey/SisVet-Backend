from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from inventario.models import Producto
from inventario.serializers import ProductoSerializer
from inventario.permissions import IsAdminOrRecepcionista


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.filter(activo=True)
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Permisos personalizados según la acción:
        - GET (list, retrieve): Cualquier usuario autenticado (incluye Veterinario)
        - POST, PUT, PATCH, DELETE: Solo Admin o Recepcionista
        """
        if self.action in ['list', 'retrieve']:
            # Solo necesita estar autenticado para ver productos
            permission_classes = [IsAuthenticated]
        else:
            # Necesita ser Admin o Recepcionista para crear/modificar/eliminar
            permission_classes = [IsAuthenticated, IsAdminOrRecepcionista]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Producto.objects.filter(activo=True)

        buscador = self.request.query_params.get("buscador")
        categoria = self.request.query_params.get("categoria")
        marca = self.request.query_params.get("marca")

        if buscador:
            queryset = queryset.filter(
                Q(nombre__icontains=buscador) |
                Q(descripcion__icontains=buscador) |
                Q(codigo_barras__icontains=buscador) |
                Q(codigo_interno__icontains=buscador)
            )

        if categoria:
            queryset = queryset.filter(
                Q(categoria__descripcion__icontains=categoria) |
                Q(categoria__id__iexact=categoria)
            )

        if marca:
            queryset = queryset.filter(
                Q(marca__descripcion__icontains=marca) |
                Q(marca__id__iexact=marca)
            )

        return queryset

#para desactivar un producto en lugar de eliminar
    def destroy(self, request, *args, **kwargs):
        producto = self.get_object()

        if not producto.activo:
            return Response(
                {"detalle": "Este producto ya está desactivado y no puede eliminarse."},
                status=status.HTTP_400_BAD_REQUEST
            )

        producto.activo = False
        producto.save()

        return Response(
            {"detalle": "Producto desactivado correctamente. Los movimientos del kardex se mantienen intactos."},
            status=status.HTTP_200_OK
        )
