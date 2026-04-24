from django.core.exceptions import ValidationError


class KardexValidator:
    """Validaciones para movimientos de Kardex."""

    @staticmethod
    def validar_producto_activo(producto):
        """
        Valida que el producto esté activo.

        Raises:
            ValidationError: Si el producto está inactivo
        """
        if not producto.activo:
            raise ValidationError(
                f"No se puede hacer movimientos del producto '{producto.nombre}' "
                f"porque está INACTIVO. Reactívalo e intente nuevamente."
            )

    @staticmethod
    def validar_movimiento_no_anulado(kardex):
        """
        Evita eliminar un movimiento ya anulado.
        """
        if kardex.detalle and "ANULADO" in kardex.detalle:
            raise ValidationError(
                "Este movimiento ya está anulado y no puede eliminarse su registro."
            )

    @staticmethod
    def validar_cantidad_positiva(cantidad):
        """
        Valida que la cantidad sea positiva.

        Raises:
            ValidationError: Si cantidad <= 0
        """
        if cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0.")

    @staticmethod
    def validar_stock_suficiente(producto, cantidad):
        """
        Valida que haya stock suficiente para salidas.

        Raises:
            ValidationError: Si no hay stock suficiente
        """
        if producto.stock < cantidad:
            raise ValidationError(
                f"Stock insuficiente. Disponible: {producto.stock}, "
                f"solicitado: {cantidad}"
            )
