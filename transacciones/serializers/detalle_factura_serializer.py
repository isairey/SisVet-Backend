from rest_framework import serializers
from transacciones.models.detalle_factura import DetalleFactura


class DetalleFacturaSerializer(serializers.ModelSerializer):
    """
    Serializer para detalles de factura.
    Incluye nombres de productos y servicios para mejor legibilidad.
    """
    producto_nombre = serializers.SerializerMethodField()
    servicio_nombre = serializers.SerializerMethodField()

    class Meta:
        model = DetalleFactura
        fields = [
            'id',
            'producto',
            'producto_nombre',
            'servicio',
            'servicio_nombre',
            'descripcion',
            'cantidad',
            'precio_unitario',
            'subtotal'
        ]
        read_only_fields = ['subtotal', 'producto_nombre', 'servicio_nombre']

    def get_producto_nombre(self, obj):
        """Retorna el nombre del producto si existe."""
        if obj.producto:
            return obj.producto.nombre
        return None

    def get_servicio_nombre(self, obj):
        """Retorna el nombre del servicio si existe."""
        if obj.servicio:
            return obj.servicio.nombre
        return None

    def validate(self, attrs):
        producto = attrs.get('producto')
        servicio = attrs.get('servicio')

        # Validación XOR
        if (producto and servicio) or (not producto and not servicio):
            raise serializers.ValidationError(
                "Debe seleccionar un producto O un servicio, pero no ambos."
            )

        return attrs