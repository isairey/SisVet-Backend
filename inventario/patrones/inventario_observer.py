"""
inventario/patrones/inventario_observer.py

Observer Pattern para el sistema de notificaciones del inventario.
Patrón: Observer (Publisher-Subscriber)
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class ObservadorInventario(ABC):
    """
    Patrón: Observer (Interfaz del Observador)

    Define la interfaz que deben implementar todos los observadores
    del inventario.
    """

    @abstractmethod
    def actualizar(self, evento: str, datos: Dict[str, Any]):
        """
        Método llamado cuando ocurre un evento en el inventario.

        Args:
            evento: Tipo de evento ('stock_bajo', 'producto_vencido', etc.)
            datos: Datos relacionados con el evento
        """
        pass


class ObservadorNotificaciones(ObservadorInventario):
    """
    Observador que crea notificaciones cuando ocurren eventos del inventario.
    """

    def actualizar(self, evento: str, datos: Dict[str, Any]):
        from inventario.services.notificacion_service import NotificacionService

        servicio = NotificacionService()
        producto = datos.get('producto')

        if not producto:
            return

        if evento == 'stock_bajo':
            servicio._verificar_stock_minimo(producto)

        elif evento == 'producto_vencido':
            servicio._verificar_vencimiento(producto)

        elif evento == 'entrada_stock':
            cantidad = datos.get('cantidad', 0)
            servicio.crear_info(
                titulo=f"Entrada de stock: {producto.nombre}",
                mensaje=f"Se agregaron {cantidad} unidades."
            )

        elif evento == 'salida_stock':
            cantidad = datos.get('cantidad', 0)
            servicio.crear_info(
                titulo=f"Salida de stock: {producto.nombre}",
                mensaje=f"Se descontaron {cantidad} unidades."
            )


class ObservadorHistorial(ObservadorInventario):
    """
    Observador que registra eventos en el historial del GestorInventario.
    """

    def actualizar(self, evento: str, datos: Dict[str, Any]):
        from .gestor_inventario import GestorInventario

        gestor = GestorInventario()
        producto = datos.get('producto')
        cantidad = datos.get('cantidad', 0)
        usuario = datos.get('usuario')

        if not producto:
            return

        # SOLO registrar eventos válidos del historial
        # Para evitar que "entrada" genere una "salida"
        eventos_validos = {
            'entrada_stock': 'ENTRADA',
            'salida_stock': 'SALIDA'
        }

        if evento not in eventos_validos:
            return

        gestor.registrar_movimiento(
            producto=producto,
            cantidad=cantidad,
            tipo=eventos_validos[evento],
            usuario=usuario
        )


class SujetoInventario:
    """
    Patrón: Observer (Sujeto/Publisher)
    Mantiene una lista de observadores y los notifica cuando ocurren eventos.
    """

    def __init__(self):
        self._observadores: List[ObservadorInventario] = []

    def agregar_observador(self, observador: ObservadorInventario):
        if observador not in self._observadores:
            self._observadores.append(observador)

    def remover_observador(self, observador: ObservadorInventario):
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar(self, evento: str, datos: Dict[str, Any]):
        for observador in self._observadores:
            try:
                observador.actualizar(evento, datos)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(
                    f"Error en observador {observador.__class__.__name__}: {e}"
                )


# Singleton
_sujeto_inventario = None


def obtener_sujeto_inventario() -> SujetoInventario:
    global _sujeto_inventario

    if _sujeto_inventario is None:
        _sujeto_inventario = SujetoInventario()

        # Observadores principales
        _sujeto_inventario.agregar_observador(ObservadorNotificaciones())
        _sujeto_inventario.agregar_observador(ObservadorHistorial())

    return _sujeto_inventario
