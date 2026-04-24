from typing import List, Dict, Optional
from datetime import date

from inventario.patrones import (
    Lote,
    GestorLotes,
    EstrategiaLoteFactory,
    obtener_sujeto_inventario
)
from inventario.models import Producto


class LoteService:
    """
    Servicio para gestionar lotes de productos.
    Integra Strategy Pattern para diferentes métodos de selección de lotes.
    """

    def __init__(self, estrategia: str = 'FIFO'):
        """
        Inicializa el servicio con una estrategia de selección.

        Args:
            estrategia: Tipo de estrategia ('FIFO', 'FEFO', 'LIFO', 'COSTO_PROMEDIO')
        """
        # Factory Pattern para crear la estrategia
        self.estrategia_actual = EstrategiaLoteFactory.crear_estrategia(estrategia)
        self.gestor_lotes = GestorLotes(self.estrategia_actual)
        self.sujeto = obtener_sujeto_inventario()

    def cambiar_estrategia(self, nueva_estrategia: str):
        """
        Cambia la estrategia de selección en tiempo de ejecución.

        Args:
            nueva_estrategia: Código de la nueva estrategia
        """
        # Factory Pattern
        self.estrategia_actual = EstrategiaLoteFactory.crear_estrategia(nueva_estrategia)
        self.gestor_lotes.cambiar_estrategia(self.estrategia_actual)

    def obtener_estrategia_actual(self) -> str:
        """Retorna el nombre de la estrategia actual."""
        return self.gestor_lotes.estrategia_actual

    @staticmethod
    def crear_lote_desde_producto(
        producto: Producto,
        cantidad: float,
        numero_lote: Optional[str] = None,
        fecha_vencimiento: Optional[date] = None,
        precio_compra: Optional[float] = None
    ) -> Lote:
        """
        Crea un objeto Lote a partir de un Producto.

        Args:
            producto: Instancia del producto
            cantidad: Cantidad del lote
            numero_lote: Número de lote (opcional)
            fecha_vencimiento: Fecha de vencimiento (opcional)
            precio_compra: Precio de compra (opcional)

        Returns:
            Instancia de Lote
        """
        return Lote(
            id=producto.id,
            producto_id=producto.id,
            producto_nombre=producto.nombre,
            cantidad=cantidad,
            fecha_ingreso=date.today(),
            fecha_vencimiento=fecha_vencimiento or producto.fecha_vencimiento,
            numero_lote=numero_lote,
            precio_compra=precio_compra or float(producto.precio_compra)
        )

    @staticmethod
    def _crear_lotes_ejemplo(cls, producto: Producto) -> list:
        """
        Crea lotes de ejemplo para demostración.
        En producción, estos lotes vendrían de una tabla en la BD.

        Args:
            producto: Producto para crear lotes

        Returns:
            Lista de lotes simulados
        """
        from datetime import timedelta

        # Dividir el stock en varios lotes simulados
        stock_total = producto.stock
        cantidad_lote_1 = stock_total * 0.4
        cantidad_lote_2 = stock_total * 0.35
        cantidad_lote_3 = stock_total * 0.25

        lotes = [
            Lote(
                id=1,
                producto_id=producto.id,
                producto_nombre=producto.nombre,
                cantidad=cantidad_lote_1,
                fecha_ingreso=date.today() - timedelta(days=30),
                fecha_vencimiento=(date.today() + timedelta(days=60)) if producto.fecha_vencimiento else None,
                numero_lote="LOTE-001",
                precio_compra=float(producto.precio_compra)
            ),
            Lote(
                id=2,
                producto_id=producto.id,
                producto_nombre=producto.nombre,
                cantidad=cantidad_lote_2,
                fecha_ingreso=date.today() - timedelta(days=15),
                fecha_vencimiento=(date.today() + timedelta(days=90)) if producto.fecha_vencimiento else None,
                numero_lote="LOTE-002",
                precio_compra=float(producto.precio_compra) * 1.05
            ),
            Lote(
                id=3,
                producto_id=producto.id,
                producto_nombre=producto.nombre,
                cantidad=cantidad_lote_3,
                fecha_ingreso=date.today() - timedelta(days=5),
                fecha_vencimiento=(date.today() + timedelta(days=120)) if producto.fecha_vencimiento else None,
                numero_lote="LOTE-003",
                precio_compra=float(producto.precio_compra) * 1.1
            ),
        ]

        return lotes

    def seleccionar_lotes_para_salida(
        self,
        lotes: List[Lote],
        cantidad_requerida: float
    ) -> List[tuple]:
        """
        Selecciona lotes para una salida de inventario usando la estrategia actual.

        Args:
            lotes: Lista de lotes disponibles
            cantidad_requerida: Cantidad total necesaria

        Returns:
            Lista de tuplas (Lote, cantidad_a_usar)
        """
        return self.gestor_lotes.seleccionar_lote_para_salida(lotes, cantidad_requerida)

    def simular_salida(
        self,
        lotes: List[Lote],
        cantidad_requerida: float,
        estrategia: Optional[str] = None
    ) -> Dict:
        """
        Simula una salida de inventario sin modificar los lotes reales.
        Útil para comparar diferentes estrategias.

        Args:
            lotes: Lista de lotes disponibles
            cantidad_requerida: Cantidad a retirar
            estrategia: Estrategia a usar (None = usar la actual)

        Returns:
            Diccionario con los resultados de la simulación
        """
        # Hacer copias de los lotes para no modificar los originales
        import copy
        lotes_copia = copy.deepcopy(lotes)

        # Usar estrategia específica o la actual
        if estrategia:
            gestor_temporal = GestorLotes(
                EstrategiaLoteFactory.crear_estrategia(estrategia)
            )
        else:
            gestor_temporal = self.gestor_lotes

        # Realizar la simulación
        resultado = gestor_temporal.seleccionar_lote_para_salida(
            lotes_copia,
            cantidad_requerida
        )

        # Calcular estadísticas
        cantidad_total = sum(cantidad for _, cantidad in resultado)
        lotes_usados = len(resultado)

        return {
            'estrategia': gestor_temporal.estrategia_actual,
            'cantidad_requerida': cantidad_requerida,
            'cantidad_obtenida': cantidad_total,
            'lotes_usados': lotes_usados,
            'detalle_lotes': [
                {
                    'lote_id': lote.id,
                    'producto': lote.producto_nombre,
                    'cantidad_usada': cantidad,
                    'fecha_vencimiento': lote.fecha_vencimiento,
                    'numero_lote': lote.numero_lote
                }
                for lote, cantidad in resultado
            ],
            'cumple_requerimiento': cantidad_total >= cantidad_requerida
        }

    def comparar_estrategias(
        self,
        lotes: List[Lote],
        cantidad_requerida: float
    ) -> Dict:
        """
        Compara todas las estrategias disponibles para una salida.

        Args:
            lotes: Lista de lotes disponibles
            cantidad_requerida: Cantidad a retirar

        Returns:
            Diccionario con resultados de todas las estrategias
        """
        resultados = {}

        for codigo, nombre in EstrategiaLoteFactory.obtener_estrategias_disponibles():
            try:
                resultado = self.simular_salida(lotes, cantidad_requerida, codigo)
                resultados[codigo] = resultado
            except Exception as e:
                resultados[codigo] = {
                    'error': str(e),
                    'estrategia': nombre
                }

        return resultados

    @staticmethod
    def obtener_estrategias_disponibles() -> List[tuple]:
        """
        Retorna las estrategias disponibles.

        Returns:
            Lista de tuplas (codigo, nombre)
        """
        return EstrategiaLoteFactory.obtener_estrategias_disponibles()