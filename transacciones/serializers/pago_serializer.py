from rest_framework import serializers
from transacciones.models.pago import Pago


class PagoSerializer(serializers.ModelSerializer):
    """
    Serializer para pagos.
    Incluye nombre del método de pago para mejor legibilidad.
    """
    metodo_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Pago
        fields = [
            'id',
            'factura',
            'metodo',
            'metodo_nombre',
            'monto',
            'fecha',
            'aprobado',
            'referencia'
        ]
        read_only_fields = ['fecha', 'metodo_nombre']

    def get_metodo_nombre(self, obj):
        """Retorna el nombre del método de pago si existe."""
        if obj.metodo:
            return obj.metodo.nombre
        return None