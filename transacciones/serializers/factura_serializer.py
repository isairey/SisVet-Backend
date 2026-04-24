from rest_framework import serializers
from transacciones.models.factura import Factura
from transacciones.serializers.detalle_factura_serializer import DetalleFacturaSerializer
from transacciones.serializers.pago_serializer import PagoSerializer


class FacturaSerializer(serializers.ModelSerializer):
    """
    Serializer para facturas.
    Incluye información completa del cliente, detalles, pagos y campos calculados.
    """
    cliente = serializers.PrimaryKeyRelatedField(read_only=True)
    cliente_nombre = serializers.SerializerMethodField()
    detalles = DetalleFacturaSerializer(many=True, read_only=True)
    pagos = PagoSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)
    impuestos = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)
    pagada = serializers.BooleanField(read_only=True)

    class Meta:
        model = Factura
        fields = [
            'id',
            'estado',
            'cliente',
            'cliente_nombre',
            'cita',
            'consulta',
            'fecha',
            'subtotal',
            'impuestos',
            'total',
            'pagada',
            'detalles',
            'pagos'
        ]
        read_only_fields = [
            'total', 'fecha', 'cliente', 'subtotal', 
            'impuestos', 'pagada', 'cliente_nombre'
        ]

    def get_cliente_nombre(self, obj):
        """Retorna el nombre completo del cliente."""
        if obj.cliente:
            return obj.cliente.get_full_name() or obj.cliente.username
        return None

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])

        factura = Factura.objects.create(**validated_data)

        # Crear detalles
        for detalle_data in detalles_data:
            DetalleFacturaSerializer().create({
                **detalle_data,
                "factura": factura
            })

        # Forzar recálculo del total
        factura.recalcular_totales()

        return factura