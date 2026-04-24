from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from inventario.models import Marca
from inventario.serializers import MarcaSerializer
from inventario.permissions import IsAdminOrRecepcionista


class MarcaViewSet(viewsets.ModelViewSet):

    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = [IsAuthenticated, IsAdminOrRecepcionista]

    def create(self, request, *args, **kwargs):
        """
        Crea una nueva marca con validaciones de normalización y duplicados.
        """
        from inventario.services.normalizacion_service import NormalizacionService
        from inventario.validators.marca_validator import MarcaValidator

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
            MarcaValidator.validar_descripcion_unica(descripcion)
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
        Actualiza una marca existente con validaciones.
        """
        from inventario.services.normalizacion_service import NormalizacionService
        from inventario.validators.marca_validator import MarcaValidator

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
            MarcaValidator.validar_descripcion_unica(nueva_desc, marca_id=instancia.pk)
        except Exception:
            return Response(
                {"mensaje": "duplicado", "campo": "descripcion"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Actualizar el valor normalizado en el request
        request.data['descripcion'] = nueva_desc
        return super().update(request, *args, **kwargs)

    def get_queryset(self):

        buscador = self.request.query_params.get("buscador")
        if buscador:
            return Marca.objects.filter(Q(descripcion__icontains=buscador))
        return Marca.objects.all()