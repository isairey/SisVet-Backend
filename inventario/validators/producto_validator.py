from decimal import Decimal
from django.core.exceptions import ValidationError
from inventario.models import Producto


class ProductoValidator:

    @staticmethod
    def validar_nombre_unico(nombre: str, producto_id=None):
        if not nombre:
            return

        qs = Producto.objects.filter(nombre__iexact=nombre)
        if producto_id:
            qs = qs.exclude(pk=producto_id)
        if qs.exists():
            raise ValidationError('Ya existe un producto con este nombre.')

    @staticmethod
    def validar_codigo_barras_unico(codigo: str, producto_id=None):
        if not codigo:
            return

        qs = Producto.objects.filter(codigo_barras__iexact=codigo)
        if producto_id:
            qs = qs.exclude(pk=producto_id)
        if qs.exists():
            raise ValidationError('Ya existe un producto con este código de barras.')

    @staticmethod
    def validar_codigo_interno_unico(codigo: str, producto_id=None):
        if not codigo:
            return

        qs = Producto.objects.filter(codigo_interno__iexact=codigo)
        if producto_id:
            qs = qs.exclude(pk=producto_id)
        if qs.exists():
            raise ValidationError('Ya existe un producto con este código interno.')

    @staticmethod
    def validar_stock_inicial(stock: Decimal, stock_minimo: Decimal):
        if stock < stock_minimo:
            raise ValidationError(
                f'El stock inicial ({stock}) debe ser mayor o igual '
                f'al stock mínimo configurado ({stock_minimo}).'
            )

    @staticmethod
    def validar_precios(precio_compra: Decimal, precio_venta: Decimal):
        if precio_venta > 0 and precio_compra >= precio_venta:
            raise ValidationError(
                f'El precio de compra ({precio_compra}) debe ser menor '
                f'al precio de venta ({precio_venta}).'
            )