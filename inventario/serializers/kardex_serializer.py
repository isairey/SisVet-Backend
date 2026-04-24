from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from inventario.models import Kardex


class KardexSerializer(serializers.ModelSerializer):
    codigo_interno = serializers.CharField(source='producto.codigo_interno', read_only=True)
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = Kardex
        fields = '__all__'
        read_only_fields = ['fecha']

    def validar_movimiento_no_anulado(self, kardex):
        """
        Evita eliminar un movimiento ya anulado.
        """
        if kardex.detalle and "ANULADO" in kardex.detalle:
            raise ValidationError(
                "Este movimiento ya está anulado y no puede eliminarse su registro."
            )

    def validate(self, data):
        """
        Valida que el producto esté activo ANTES de que se guarde el Kardex.
        Esto asegura que el error salga en formato JSON y no como HTML.
        """
        producto = data.get("producto")

        if producto and not producto.activo:
            raise ValidationError(
                f"No se puede hacer movimientos del producto '{producto.nombre}' "
                f"porque está INACTIVO. Reactívalo e intente nuevamente."
            )

        return data
