from inventario.models import Producto
from inventario.patrones import obtener_sujeto_inventario
from inventario.services.notificacion_service import NotificacionService


class StockService:
    """
    Servicio responsable de todas las operaciones relacionadas con el stock.
    Ahora integra el patrón Observer para notificaciones automáticas.
    """

    def __init__(self):
        self.notificaciones = NotificacionService()
        self.sujeto = obtener_sujeto_inventario()  # Observer Pattern

    def agregar_stock(self, producto: Producto, cantidad: int, usuario=None) -> None:
        """
        Agrega stock a un producto.
        """

        cantidad = int(cantidad)
        producto.stock += cantidad
        producto.save(update_fields=['stock'])

        # Notificar SOLO entrada
        self.sujeto.notificar('entrada_stock', {
            'producto': producto,
            'cantidad': cantidad,
            'usuario': usuario
        })

        # Verificar alertas
        self.sujeto.notificar('stock_bajo', {'producto': producto})
        self.sujeto.notificar('producto_vencido', {'producto': producto})

    def restar_stock(self, producto: Producto, cantidad: int) -> None:
        """
        Resta stock de un producto.
        """

        cantidad = int(cantidad)

        if producto.stock < cantidad:
            raise ValueError(
                f"Stock insuficiente para el producto '{producto.nombre}'. "
                f"Stock actual: {producto.stock}, solicitado: {cantidad}"
            )

        producto.stock -= cantidad
        producto.save(update_fields=['stock'])

        # Notificar SOLO salida
        self.sujeto.notificar('salida_stock', {
            'producto': producto,
            'cantidad': cantidad,
        })

        # Verificar alertas
        self.sujeto.notificar('stock_bajo', {'producto': producto})
        self.sujeto.notificar('producto_vencido', {'producto': producto})
