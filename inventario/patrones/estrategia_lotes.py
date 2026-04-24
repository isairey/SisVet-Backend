from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Lote:
    """
    Representa un lote de productos en el inventario.
    """
    id: int
    producto_id: int
    producto_nombre: str
    cantidad: float
    fecha_ingreso: date
    fecha_vencimiento: Optional[date] = None
    numero_lote: Optional[str] = None
    precio_compra: float = 0.0

    @property
    def dias_hasta_vencimiento(self) -> Optional[int]:
        """Calcula días hasta el vencimiento."""
        if self.fecha_vencimiento:
            return (self.fecha_vencimiento - date.today()).days
        return None

    @property
    def esta_vencido(self) -> bool:
        """Verifica si el lote está vencido."""
        if self.fecha_vencimiento:
            return self.fecha_vencimiento < date.today()
        return False


class EstrategiaSeleccionLote(ABC):
    """
    Patrón: Strategy (Interfaz base)

    Define la interfaz para estrategias de selección de lotes.
    """

    @abstractmethod
    def seleccionar_lote(self, lotes: List[Lote]) -> Optional[Lote]:
        """
        Selecciona un lote según la estrategia implementada.

        Args:
            lotes: Lista de lotes disponibles

        Returns:
            Lote seleccionado o None si no hay lotes disponibles
        """
        pass

    @abstractmethod
    def nombre_estrategia(self) -> str:
        """Retorna el nombre de la estrategia."""
        pass


class EstrategiaFIFO(EstrategiaSeleccionLote):
    """
    Patrón: Strategy (Implementación concreta)

    First In, First Out - El primer lote en entrar es el primero en salir.
    Ideal para productos no perecederos.
    """

    def seleccionar_lote(self, lotes: List[Lote]) -> Optional[Lote]:
        """
        Selecciona el lote más antiguo (por fecha de ingreso).

        Args:
            lotes: Lista de lotes disponibles

        Returns:
            Lote más antiguo con stock disponible
        """
        if not lotes:
            return None

        # Filtrar lotes con stock disponible
        lotes_disponibles = [l for l in lotes if l.cantidad > 0]

        if not lotes_disponibles:
            return None

        # Ordenar por fecha de ingreso (más antiguo primero)
        return sorted(lotes_disponibles, key=lambda l: l.fecha_ingreso)[0]

    def nombre_estrategia(self) -> str:
        return "FIFO (First In, First Out)"


class EstrategiaFEFO(EstrategiaSeleccionLote):
    """
    Patrón: Strategy (Implementación concreta)

    First Expired, First Out - El lote que vence primero sale primero.
    """

    def seleccionar_lote(self, lotes: List[Lote]) -> Optional[Lote]:
        """
        Selecciona el lote con fecha de vencimiento más próxima.

        Args:
            lotes: Lista de lotes disponibles

        Returns:
            Lote con vencimiento más próximo
        """
        if not lotes:
            return None

        # Filtrar lotes con stock disponible y no vencidos
        lotes_disponibles = [
            l for l in lotes
            if l.cantidad > 0 and not l.esta_vencido
        ]

        if not lotes_disponibles:
            return None

        # Ordenar por fecha de vencimiento (más próximo primero)
        # Los lotes sin fecha de vencimiento van al final
        return sorted(
            lotes_disponibles,
            key=lambda l: l.fecha_vencimiento or date.max
        )[0]

    def nombre_estrategia(self) -> str:
        return "FEFO (First Expired, First Out)"


class EstrategiaLIFO(EstrategiaSeleccionLote):
    """
    Patrón: Strategy (Implementación concreta)

    Last In, First Out - El último lote en entrar es el primero en salir.
    Menos común, útil en casos específicos de almacenamiento.
    """

    def seleccionar_lote(self, lotes: List[Lote]) -> Optional[Lote]:
        """
        Selecciona el lote más reciente (por fecha de ingreso).

        Args:
            lotes: Lista de lotes disponibles

        Returns:
            Lote más reciente con stock disponible
        """
        if not lotes:
            return None

        # Filtrar lotes con stock disponible
        lotes_disponibles = [l for l in lotes if l.cantidad > 0]

        if not lotes_disponibles:
            return None

        # Ordenar por fecha de ingreso (más reciente primero)
        return sorted(lotes_disponibles, key=lambda l: l.fecha_ingreso, reverse=True)[0]

    def nombre_estrategia(self) -> str:
        return "LIFO (Last In, First Out)"


class EstrategiaCostoPromedio(EstrategiaSeleccionLote):
    """
    Patrón: Strategy (Implementación concreta)

    Selecciona lotes basándose en el costo promedio.
    Útil para valorización de inventario.
    """

    def seleccionar_lote(self, lotes: List[Lote]) -> Optional[Lote]:
        """
        Selecciona el lote con precio más cercano al promedio.

        Args:
            lotes: Lista de lotes disponibles

        Returns:
            Lote con precio más cercano al promedio
        """
        if not lotes:
            return None

        # Filtrar lotes con stock disponible
        lotes_disponibles = [l for l in lotes if l.cantidad > 0]

        if not lotes_disponibles:
            return None

        # Calcular precio promedio
        precio_promedio = sum(l.precio_compra for l in lotes_disponibles) / len(lotes_disponibles)

        # Seleccionar lote con precio más cercano al promedio
        return min(lotes_disponibles, key=lambda l: abs(l.precio_compra - precio_promedio))

    def nombre_estrategia(self) -> str:
        return "Costo Promedio"


class GestorLotes:
    """
    Context del patrón Strategy.
    Gestiona la selección de lotes usando diferentes estrategias.
    """

    def __init__(self, estrategia: EstrategiaSeleccionLote):
        """
        Inicializa el gestor con una estrategia específica.
        """
        self._estrategia = estrategia

    def cambiar_estrategia(self, estrategia: EstrategiaSeleccionLote):
        """
        Cambia la estrategia de selección en tiempo de ejecución.
        """
        self._estrategia = estrategia

    def seleccionar_lote_para_salida(self, lotes: List[Lote], cantidad_requerida: float) -> List[tuple]:
        """
        Selecciona uno o más lotes para satisfacer una cantidad requerida.
        """
        resultado = []
        cantidad_pendiente = cantidad_requerida
        lotes_restantes = lotes.copy()

        while cantidad_pendiente > 0 and lotes_restantes:
            lote_seleccionado = self._estrategia.seleccionar_lote(lotes_restantes)

            if not lote_seleccionado:
                break

            # Calcular cuánto tomar de este lote
            cantidad_a_usar = min(lote_seleccionado.cantidad, cantidad_pendiente)

            resultado.append((lote_seleccionado, cantidad_a_usar))

            # Actualizar cantidades
            cantidad_pendiente -= cantidad_a_usar
            lote_seleccionado.cantidad -= cantidad_a_usar

            # Si el lote se agotó, quitarlo de la lista
            if lote_seleccionado.cantidad <= 0:
                lotes_restantes.remove(lote_seleccionado)

        return resultado

    @property
    def estrategia_actual(self) -> str:
        """Retorna el nombre de la estrategia actual."""
        return self._estrategia.nombre_estrategia()