from .estrategia_lotes import (
    EstrategiaSeleccionLote,
    EstrategiaFIFO,
    EstrategiaFEFO,
    EstrategiaLIFO,
    EstrategiaCostoPromedio
)


class EstrategiaLoteFactory:


    # Registro de estrategias disponibles
    _estrategias = {
        'FIFO': EstrategiaFIFO,
        'FEFO': EstrategiaFEFO,
        'LIFO': EstrategiaLIFO,
        'COSTO_PROMEDIO': EstrategiaCostoPromedio,
    }

    @classmethod
    def crear_estrategia(cls, tipo_estrategia: str) -> EstrategiaSeleccionLote:
        """
        Crea una instancia de la estrategia solicitada.

        Args:
            tipo_estrategia: Tipo de estrategia ('FIFO', 'FEFO', 'LIFO', 'COSTO_PROMEDIO')

        Returns:
            Instancia de la estrategia solicitada

        Raises:
            ValueError: Si el tipo de estrategia no existe
        """
        tipo_estrategia = tipo_estrategia.upper()

        if tipo_estrategia not in cls._estrategias:
            raise ValueError(
                f"Estrategia '{tipo_estrategia}' no existe. "
                f"Estrategias disponibles: {', '.join(cls._estrategias.keys())}"
            )

        estrategia_class = cls._estrategias[tipo_estrategia]
        return estrategia_class()

    @classmethod
    def obtener_estrategias_disponibles(cls) -> list:
        """
        Retorna la lista de estrategias disponibles.

        Returns:
            Lista de tuplas (codigo, nombre_legible)
        """
        return [
            ('FIFO', 'FIFO - First In, First Out'),
            ('FEFO', 'FEFO - First Expired, First Out'),
            ('LIFO', 'LIFO - Last In, First Out'),
            ('COSTO_PROMEDIO', 'Costo Promedio'),
        ]

    @classmethod
    def registrar_estrategia(cls, codigo: str, clase_estrategia):
        """
        Permite registrar nuevas estrategias dinámicamente.
        """
        if not issubclass(clase_estrategia, EstrategiaSeleccionLote):
            raise TypeError(
                f"La clase {clase_estrategia.__name__} debe heredar de EstrategiaSeleccionLote"
            )

        cls._estrategias[codigo.upper()] = clase_estrategia

    @classmethod
    def estrategia_por_defecto(cls) -> EstrategiaSeleccionLote:
        """
        Retorna la estrategia por defecto (FIFO).

        Returns:
            Instancia de EstrategiaFIFO
        """
        return cls.crear_estrategia('FIFO')