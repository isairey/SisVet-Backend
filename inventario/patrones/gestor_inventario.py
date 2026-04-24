import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class GestorInventario:
    """
    Patrón: Singleton

    Gestor centralizado del inventario que garantiza una única instancia
    para coordinar todas las operaciones críticas del sistema.
    """
    _instancia: Optional['GestorInventario'] = None
    _inicializado: bool = False

    def __new__(cls):
        """
        Garantiza que solo exista una instancia del gestor.
        """
        if cls._instancia is None:
            cls._instancia = super(GestorInventario, cls).__new__(cls)
        return cls._instancia

    def __init__(self):
        """
        Inicializa el gestor solo una vez.
        """
        if not self._inicializado:
            self._historial_operaciones = []
            self._inicializado = True
            logger.info("GestorInventario inicializado (Singleton)")

    def registrar_movimiento(self, producto, cantidad, tipo: str, usuario=None):
        """
        Registra un movimiento en el inventario.

        Args:
            producto: Instancia del producto
            cantidad: Cantidad del movimiento
            tipo: Tipo de movimiento (ENTRADA, SALIDA, MODIFICACIÓN, etc.)
            usuario: Usuario que realiza la operación (opcional)
        """
        operacion = {
            'timestamp': datetime.now(),
            'producto': producto.nombre,
            'producto_id': producto.id,
            'cantidad': cantidad,
            'tipo': tipo,
            'usuario': usuario.username if usuario else 'Sistema',
            'stock_resultante': producto.stock
        }

        self._historial_operaciones.append(operacion)

        logger.info(
            f"{tipo}: {cantidad} unidades de '{producto.nombre}' "
            f"| Stock resultante: {producto.stock} "
            f"| Usuario: {operacion['usuario']}"
        )

    def obtener_historial(self, limite: int = 100):
        """
        Obtiene el historial de operaciones recientes.

        Args:
            limite: Número máximo de operaciones a retornar

        Returns:
            Lista de operaciones recientes
        """
        return self._historial_operaciones[-limite:]

    def obtener_operaciones_producto(self, producto_id: int):
        """
        Obtiene todas las operaciones de un producto específico.

        Args:
            producto_id: ID del producto

        Returns:
            Lista de operaciones del producto
        """
        return [
            op for op in self._historial_operaciones
            if op['producto_id'] == producto_id
        ]

    def limpiar_historial(self):
        """
        Limpia el historial de operaciones.
        Útil para mantenimiento o pruebas.
        """
        self._historial_operaciones.clear()
        logger.info("Historial de operaciones limpiado")

    @classmethod
    def reiniciar_instancia(cls):
        """
        Reinicia el singleton (útil para tests).
        ⚠️ Usar solo en entorno de desarrollo/testing.
        """
        cls._instancia = None
        cls._inicializado = False
        logger.warning("GestorInventario reiniciado (solo para testing)")