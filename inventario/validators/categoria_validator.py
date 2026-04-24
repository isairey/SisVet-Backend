
from django.core.exceptions import ValidationError
from inventario.models import Categoria


class CategoriaValidator:


    @staticmethod
    def validar_descripcion_unica(descripcion: str, categoria_id=None):

        qs = Categoria.objects.filter(descripcion__iexact=descripcion)

        if categoria_id:
            qs = qs.exclude(pk=categoria_id)

        if qs.exists():
            raise ValidationError('Ya existe una categoría con este nombre.')