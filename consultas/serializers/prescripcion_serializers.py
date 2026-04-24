"""
Serializers para el modelo Prescripcion.
"""

from rest_framework import serializers
from consultas.models import Prescripcion

MEDICAMENTO_nombre = 'medicamento.nombre'
MEDICAMENTO_descripcion = 'medicamento.descripcion'
MEDICAMENTO_stock = 'medicamento.stock'


class PrescripcionListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar prescripciones.
    """
    producto_nombre = serializers.CharField(
        source=MEDICAMENTO_nombre,
        read_only=True
    )

    producto_descripcion = serializers.CharField(
        source=MEDICAMENTO_descripcion,
        read_only=True
    )

    class Meta:
        model = Prescripcion
        fields = [
            'id',
            'medicamento',
            'producto_nombre',
            'producto_descripcion',
            'cantidad',
            'indicaciones',
        ]

class PrescripcionSerializer(serializers.ModelSerializer):
    """
    Incluye información detallada del producto (medicamento) completo para lectura de prescripciones.
    """
    producto_nombre = serializers.CharField(
        source=MEDICAMENTO_nombre,
        read_only=True
    )

    producto_descripcion = serializers.CharField(
        source=MEDICAMENTO_descripcion,
        read_only=True
    )

    stock_disponible = serializers.IntegerField(
        source=MEDICAMENTO_stock,
        read_only=True
    )

    class Meta:
        model = Prescripcion
        fields = [
            'id',
            'consulta',
            'medicamento',  # FK → Producto
            'producto_nombre',
            'producto_descripcion',
            'cantidad',
            'stock_disponible',
            'indicaciones',
            'fecha_prescripcion',
        ]
        read_only_fields = ['id', 'fecha_prescripcion']


class PrescripcionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear prescripciones.
    """

    producto_nombre = serializers.CharField(
        source=MEDICAMENTO_nombre,
        read_only=True
    )

    stock_disponible = serializers.IntegerField(
        source=MEDICAMENTO_stock,
        read_only=True
    )

    class Meta:
        model = Prescripcion
        fields = [
            'medicamento',
            'producto_nombre',
            'cantidad',
            'stock_disponible',
            'indicaciones',
        ]

    def validate_medicamento(self, value):
        """
        Valida que el producto esté disponible y no vencido.
        """
        if not value:
            raise serializers.ValidationError("Debe seleccionar un producto del inventario")

        # Validar que no esté vencido
        if hasattr(value, "esta_vencido") and value.esta_vencido():
            raise serializers.ValidationError(
                f"El producto '{value.nombre}' está vencido. "
                f"Fecha de vencimiento: {value.fecha_vencimiento.strftime('%d/%m/%Y')}"
            )

        return value

    def validate_cantidad(self, value):
        """Valida que la cantidad sea al menos 1"""
        if value < 1:
            raise serializers.ValidationError("La cantidad debe ser al menos 1")
        return value

    def validate(self, data):
        """
        Validación cruzada: producto vs cantidad.
        """
        producto = data.get('medicamento')
        cantidad = data.get('cantidad')

        if producto and cantidad and producto.stock < cantidad:
            raise serializers.ValidationError({
                'cantidad': (
                    f'Stock insuficiente. Solo hay {producto.stock} '
                    f'unidades disponibles de {producto.descripcion}'
                )
            })

        return data

    def to_representation(self, instance):
        """Usar el serializer completo para la respuesta"""
        return PrescripcionSerializer(instance).data
