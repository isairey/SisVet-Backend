from rest_framework.exceptions import ValidationError

from inventario.patrones import GestorInventario
from inventario.validators.kardex_validator import KardexValidator


class KardexService:
    """
    Servicio que procesa los movimientos de Kardex.

    Responsabilidades:
    - Validar que el producto esté activo
    - Actualizar stock
    - Crear notificaciones
    - Registrar en GestorInventario
    """

    def __init__(self):
        from inventario.services.stock_service import StockService
        from inventario.services.notificacion_service import NotificacionService

        self.stock_service = StockService()
        self.notificacion_service = NotificacionService()
        self.gestor = GestorInventario()
        self.validator = KardexValidator()

    def procesar_movimiento(self, kardex, usuario=None):
        """
        Procesa un movimiento de Kardex (entrada o salida).
        """
        producto = kardex.producto
        cantidad = int(kardex.cantidad)

        #  Validar que el producto esté ACTIVO
        self.validator.validar_producto_activo(producto)

        #  Validar cantidad positiva
        self.validator.validar_cantidad_positiva(cantidad)

        #  Validar stock suficiente para salidas
        if kardex.tipo == 'salida':
            self.validator.validar_stock_suficiente(producto, cantidad)

        print(f"Validaciones OK - Procesando {kardex.tipo}")

        #  Actualizar stock según el tipo
        if kardex.tipo == 'entrada':
            self.stock_service.agregar_stock(producto, cantidad)
        elif kardex.tipo == 'salida':
            self.stock_service.restar_stock(producto, cantidad)

        # NOTIFICACIÓN DEL MOVIMIENTO (AGREGADA)
        self.notificacion_service.crear_info(
            f"Movimiento registrado: {producto.nombre}",
            f"Se realizó una {kardex.tipo} de {cantidad} unidades del producto '{producto.nombre}'."
        )

        #  Verificar alertas
        self.notificacion_service.verificar_alertas_producto(producto)

        #  Registrar en Singleton
        self.gestor.registrar_movimiento(
            producto=producto,
            cantidad=cantidad,
            tipo=f"KARDEX_{kardex.tipo.upper()}",
            usuario=usuario
        )

    def anular_movimiento(self, kardex, usuario=None):
        """
        Anula un movimiento de Kardex (revierte los cambios).
        """
        # Evitar anular dos veces
        if kardex.detalle and "ANULADO" in kardex.detalle:
            raise ValidationError("No se puede eliminar o anular un movimiento que ya está ANULADO.")

        producto = kardex.producto
        cantidad = int(kardex.cantidad)

        # Revertir efecto en stock (sin validar si está activo)
        if kardex.tipo == 'entrada':
            self.stock_service.restar_stock(producto, cantidad)
        elif kardex.tipo == 'salida':
            self.stock_service.agregar_stock(producto, cantidad)

        # Marcar como ANULADO
        kardex.detalle = f"{kardex.detalle or ''} - ANULADO"
        kardex.save(update_fields=['detalle'])

        # NOTIFICACIÓN DE ANULACIÓN (AGREGADA)
        self.notificacion_service.crear_warning(
            f"Movimiento anulado: {producto.nombre}",
            f"Se anuló un movimiento de tipo {kardex.tipo} por {cantidad} unidades del producto '{producto.nombre}'."
        )

        # Verificar alertas
        self.notificacion_service.verificar_alertas_producto(producto)

        # Registrar en Singleton
        self.gestor.registrar_movimiento(
            producto=producto,
            cantidad=cantidad,
            tipo=f"ANULACIÓN_{kardex.tipo.upper()}",
            usuario=usuario
        )
