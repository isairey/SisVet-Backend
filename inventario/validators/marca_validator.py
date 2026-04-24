from django.core.exceptions import ValidationError
from inventario.models import Marca


class MarcaValidator:
    """
    Validaciones de negocio para Marca.
    """

    @staticmethod
    def validar_descripcion_unica(descripcion: str, marca_id=None):

        qs = Marca.objects.filter(descripcion__iexact=descripcion)

        if marca_id:
            qs = qs.exclude(pk=marca_id)

        if qs.exists():
            raise ValidationError('Ya existe una marca con este nombre.')