from rest_framework import serializers
from inventario.models import Producto, Marca, Categoria
from inventario.services.producto_service import ProductoService
from .marca_serializer import MarcaSerializer
from .categoria_serializer import CategoriaSerializer


class ProductoSerializer(serializers.ModelSerializer):
    marca = MarcaSerializer(read_only=True)
    categoria = CategoriaSerializer(read_only=True)

    marca_id = serializers.PrimaryKeyRelatedField(
        queryset=Marca.objects.all(),
        source='marca',
        write_only=True,
        required=False
    )
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        source='categoria',
        write_only=True,
        required=False
    )

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'marca', 'categoria',
            'marca_id', 'categoria_id', 'stock', 'stock_minimo',
            'codigo_barras', 'codigo_interno', 'precio_venta',
            'precio_compra', 'fecha_vencimiento','activo'
        ]

    def validate(self, data):
        service = ProductoService()
        producto_id = self.instance.id if self.instance else None

        errores = service.validar_datos_producto(data, producto_id)

        if errores:
            raise serializers.ValidationError(errores)

        # Normalización de los datos
        normalizados = service.normalizar_datos_producto(data)
        data.update(normalizados)

        return data
