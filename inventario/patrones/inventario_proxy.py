from typing import Optional
from django.contrib.auth.models import User
from inventario.models import Producto
from .gestor_inventario import GestorInventario


class InventarioProxy:
    """
    Patrón: Proxy

    Controla y valida el acceso a operaciones críticas del inventario.
    Actúa como intermediario entre el usuario y el gestor real.
    """

    def __init__(self, usuario: Optional[User] = None):
        """
        Inicializa el proxy con un usuario específico.

        Args:
            usuario: Usuario que realizará las operaciones
        """
        self.usuario = usuario
        self.gestor = GestorInventario()

    def modificar_stock(self, producto: Producto, cantidad: float, motivo: str = ""):
        """
        Modifica el stock directamente (requiere permisos de staff).

        Args:
            producto: Producto a modificar
            cantidad: Cantidad a agregar o restar
            motivo: Motivo de la modificación
        """
        # Validar permisos
        self._validar_permisos_staff()

        # Validar cantidad
        if cantidad == 0:
            raise ValueError("La cantidad debe ser diferente de cero")

        # Validar stock suficiente si es una resta
        if cantidad < 0 and producto.stock < abs(cantidad):
            raise ValueError(
                f"Stock insuficiente. Actual: {producto.stock}, "
                f"Solicitado: {abs(cantidad)}"
            )

        # Modificar stock
        stock_anterior = producto.stock
        producto.stock += cantidad
        producto.save(update_fields=['stock'])

        # Registrar en el gestor
        tipo_operacion = "MODIFICACIÓN +" if cantidad > 0 else "MODIFICACIÓN -"
        self.gestor.registrar_movimiento(
            producto=producto,
            cantidad=abs(cantidad),
            tipo=f"{tipo_operacion} ({motivo or 'Sin motivo'})",
            usuario=self.usuario
        )

        return {
            'producto': producto.nombre,
            'stock_anterior': stock_anterior,
            'stock_nuevo': producto.stock,
            'cantidad_modificada': cantidad,
            'usuario': self.usuario.username if self.usuario else 'Sistema'
        }

    def consultar_stock(self, producto: Producto) -> dict:
        """
        Consulta el stock de un producto (sin restricciones).
        """
        return {
            'producto': producto.nombre,
            'stock_actual': producto.stock,
            'stock_minimo': producto.stock_minimo,
            'estado': 'CRÍTICO' if producto.stock <= producto.stock_minimo else 'NORMAL',
            'puede_vender': producto.stock > 0
        }

    def ajustar_inventario(self, producto: Producto, stock_real: float, motivo: str):
        """
        Ajusta el stock basándose en un conteo físico (requiere permisos).
        """
        self._validar_permisos_staff()

        diferencia = stock_real - producto.stock

        if diferencia == 0:
            return {
                'mensaje': 'No hay diferencia entre stock físico y sistema',
                'producto': producto.nombre
            }

        stock_anterior = producto.stock
        producto.stock = stock_real
        producto.save(update_fields=['stock'])

        # Registrar en el gestor
        self.gestor.registrar_movimiento(
            producto=producto,
            cantidad=abs(diferencia),
            tipo=f"AJUSTE INVENTARIO: {motivo}",
            usuario=self.usuario
        )

        return {
            'producto': producto.nombre,
            'stock_sistema': stock_anterior,
            'stock_fisico': stock_real,
            'diferencia': diferencia,
            'tipo_ajuste': 'FALTANTE' if diferencia < 0 else 'SOBRANTE'
        }

    def _validar_permisos_staff(self):
        """
        Valida que el usuario tenga permisos de staff.
        """
        if not self.usuario:
            raise PermissionError(
                "Se requiere un usuario autenticado para realizar esta operación"
            )

        if not self.usuario.is_staff:
            raise PermissionError(
                f"El usuario '{self.usuario.username}' no tiene permisos "
                f"para realizar operaciones administrativas de inventario"
            )

    def obtener_historial_operaciones(self, limite: int = 50):
        """
        Obtiene el historial de operaciones (requiere permisos).
        """
        self._validar_permisos_staff()
        return self.gestor.obtener_historial(limite)