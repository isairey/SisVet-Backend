from rest_framework import serializers


class ProductoFacturaSerializer(serializers.Serializer):
    """
    Serializer para validar los datos de un producto en la creación de factura desde inventario.
    """
    producto_id = serializers.IntegerField(required=True, min_value=1)
    cantidad = serializers.IntegerField(required=True, min_value=1)

    def validate_producto_id(self, value):
        """Valida que el producto exista y esté activo."""
        from inventario.models import Producto
        try:
            producto = Producto.objects.get(id=value, activo=True)
        except Producto.DoesNotExist:
            raise serializers.ValidationError(
                f"El producto con ID {value} no existe o está inactivo."
            )
        return value


class CrearFacturaDesdeProductosSerializer(serializers.Serializer):
    """
    Serializer para crear una factura desde productos (venta directa desde inventario).
    """
    cliente_id = serializers.IntegerField(required=True, min_value=1)
    productos = ProductoFacturaSerializer(many=True, required=True, min_length=1)

    def validate_cliente_id(self, value):
        """Valida que el cliente exista."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("El cliente no existe.")
        return value

    def validate_productos(self, value):
        """Valida que no haya productos duplicados."""
        producto_ids = [item['producto_id'] for item in value]
        if len(producto_ids) != len(set(producto_ids)):
            raise serializers.ValidationError(
                "No se pueden incluir productos duplicados en la misma factura."
            )
        return value

