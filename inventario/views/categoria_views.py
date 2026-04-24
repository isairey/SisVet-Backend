from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from inventario.models import Categoria
from inventario.serializers import CategoriaSerializer
from inventario.permissions import IsAdminOrRecepcionista


class CategoriaViewSet(viewsets.ModelViewSet):

    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated, IsAdminOrRecepcionista]

    def create(self, request, *args, **kwargs):
        """
        Crea una nueva categoría con validaciones de normalización y duplicados.
        """
        from inventario.services.normalizacion_service import NormalizacionService
        from inventario.validators.categoria_validator import CategoriaValidator

        descripcion = request.data.get("descripcion", "").strip()

        # Validar campo requerido
        if not descripcion:
            return Response(
                {"mensaje": "La descripción es requerida"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Normalizar
        descripcion = NormalizacionService.normalizar_texto(descripcion)

        # Validar duplicados
        try:
            CategoriaValidator.validar_descripcion_unica(descripcion)
        except Exception:
            return Response(
                {"mensaje": "duplicado", "campo": "descripcion"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Actualizar el valor normalizado en el request
        request.data['descripcion'] = descripcion
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Actualiza una categoría existente con validaciones.
        """
        from inventario.services.normalizacion_service import NormalizacionService
        from inventario.validators.categoria_validator import CategoriaValidator

        instancia = self.get_object()
        nueva_desc = request.data.get("descripcion", "").strip()

        # Validar campo requerido
        if not nueva_desc:
            return Response(
                {"mensaje": "La descripción es requerida"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Normalizar
        nueva_desc = NormalizacionService.normalizar_texto(nueva_desc)

        # Validar duplicados excluyendo la instancia actual
        try:
            CategoriaValidator.validar_descripcion_unica(nueva_desc, categoria_id=instancia.pk)
        except Exception:
            return Response(
                {"mensaje": "duplicado", "campo": "descripcion"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Actualizar el valor normalizado en el request
        request.data['descripcion'] = nueva_desc
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        """
        Filtra categorías por buscador si se proporciona.
        """
        buscador = self.request.query_params.get("buscador")
        if buscador:
            return Categoria.objects.filter(Q(descripcion__icontains=buscador))
        return Categoria.objects.all()