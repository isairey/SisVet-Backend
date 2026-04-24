from .gestor_inventario import GestorInventario


# PROXY PATTERN
from .inventario_proxy import InventarioProxy

# STRATEGY PATTERN
from .estrategia_lotes import (
    Lote,
    EstrategiaSeleccionLote,
    EstrategiaFIFO,
    EstrategiaFEFO,
    EstrategiaLIFO,
    EstrategiaCostoPromedio,
    GestorLotes
)

# FACTORY PATTERN
from .estrategia_factory import EstrategiaLoteFactory


# OBSERVER PATTERN

from .inventario_observer import (
    ObservadorInventario,
    ObservadorNotificaciones,
    ObservadorHistorial,
    SujetoInventario,
    obtener_sujeto_inventario
)

# EXPORTS
__all__ = [
    # Singleton
    'GestorInventario',

    # Proxy
    'InventarioProxy',

    # Strategy
    'Lote',
    'EstrategiaSeleccionLote',
    'EstrategiaFIFO',
    'EstrategiaFEFO',
    'EstrategiaLIFO',
    'EstrategiaCostoPromedio',
    'GestorLotes',
    
    # Factory
    'EstrategiaLoteFactory',
    
    # Observer
    'ObservadorInventario',
    'ObservadorNotificaciones',
    'ObservadorHistorial',
    'SujetoInventario',
    'obtener_sujeto_inventario',
]