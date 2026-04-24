"""
inventario/views/lote_views.py

ViewSet para gestionar lotes usando Strategy Pattern.
Endpoints para usar las estrategias de selección de lotes
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import date

from inventario.models import Producto
from inventario.services.lote_service import LoteService
from inventario.patrones import Lote
from inventario.permissions import IsAdminOrRecepcionista


# Constantes para mensajes de error
ERROR_CAMPOS_REQUERIDOS = 'Se requiere producto_id y cantidad_requerida'
ERROR_PRODUCTO_NO_ENCONTRADO = 'Producto no encontrado'


class LoteViewSet(viewsets.ViewSet):
    """
    ViewSet para operaciones con lotes y estrategias de selección.
    Demuestra el uso de Strategy Pattern + Factory Pattern.
    """
    permission_classes = [IsAuthenticated, IsAdminOrRecepcionista]

    @action(detail=False, methods=['get'])
    def estrategias_disponibles(self, request):
        """
        GET /api/lotes/estrategias_disponibles/

        Retorna todas las estrategias de selección disponibles.
        """
        estrategias = LoteService.obtener_estrategias_disponibles()

        return Response({
            'estrategias': [
                {'codigo': codigo, 'nombre': nombre}
                for codigo, nombre in estrategias
            ]
        })

    @action(detail=False, methods=['post'])
    def simular_salida(self, request):
        """
        POST /api/lotes/simular_salida/

        Simula una salida de inventario con una estrategia específica.

        Body:
        {
            "producto_id": 1,
            "cantidad_requerida": 100,
            "estrategia": "FIFO"  // opcional, por defecto FIFO
        }
        """
        producto_id = request.data.get('producto_id')
        cantidad_requerida = request.data.get('cantidad_requerida')
        estrategia = request.data.get('estrategia', 'FIFO')

        # Validaciones
        if not producto_id or not cantidad_requerida:
            return Response(
                {'error': ERROR_CAMPOS_REQUERIDOS},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            producto = Producto.objects.get(id=producto_id, activo=True)
        except Producto.DoesNotExist:
            return Response(
                {'error': ERROR_PRODUCTO_NO_ENCONTRADO},
                status=status.HTTP_404_NOT_FOUND
            )

        # Crear lotes simulados (en producción, estos vendrían de la BD)
        lotes = self._crear_lotes_ejemplo(producto)

        # Simular la salida
        try:
            servicio = LoteService(estrategia=estrategia)
            resultado = servicio.simular_salida(lotes, float(cantidad_requerida))

            return Response(resultado)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def comparar_estrategias(self, request):
        """
        POST /api/lotes/comparar_estrategias/

        Compara todas las estrategias para una salida específica.

        Body:
        {
            "producto_id": 1,
            "cantidad_requerida": 100
        }
        """
        producto_id = request.data.get('producto_id')
        cantidad_requerida = request.data.get('cantidad_requerida')

        if not producto_id or not cantidad_requerida:
            return Response(
                {'error': ERROR_CAMPOS_REQUERIDOS},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            producto = Producto.objects.get(id=producto_id, activo=True)
        except Producto.DoesNotExist:
            return Response(
                {'error': ERROR_PRODUCTO_NO_ENCONTRADO},
                status=status.HTTP_404_NOT_FOUND
            )

        # Crear lotes de ejemplo
        lotes = self._crear_lotes_ejemplo(producto)

        # Comparar estrategias
        servicio = LoteService()
        comparacion = servicio.comparar_estrategias(lotes, float(cantidad_requerida))

        return Response({
            'producto': producto.nombre,
            'cantidad_requerida': cantidad_requerida,
            'stock_actual': producto.stock,
            'comparacion': comparacion
        })

    @action(detail=False, methods=['post'])
    def seleccionar_lotes(self, request):
        """
        POST /api/lotes/seleccionar_lotes/

        Selecciona los lotes óptimos para una salida usando una estrategia.

        Body:
        {
            "producto_id": 1,
            "cantidad_requerida": 100,
            "estrategia": "FEFO"
        }
        """
        producto_id = request.data.get('producto_id')
        cantidad_requerida = request.data.get('cantidad_requerida')
        estrategia = request.data.get('estrategia', 'FIFO')

        if not producto_id or not cantidad_requerida:
            return Response(
                {'error': ERROR_CAMPOS_REQUERIDOS},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            producto = Producto.objects.get(id=producto_id, activo=True)
        except Producto.DoesNotExist:
            return Response(
                {'error': ERROR_PRODUCTO_NO_ENCONTRADO},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validar stock suficiente
        if producto.stock < float(cantidad_requerida):
            return Response(
                {
                    'error': 'Stock insuficiente',
                    'stock_disponible': producto.stock,
                    'cantidad_requerida': cantidad_requerida
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear lotes de ejemplo
        lotes = self._crear_lotes_ejemplo(producto)

        # Seleccionar lotes
        try:
            servicio = LoteService(estrategia=estrategia)
            lotes_seleccionados = servicio.seleccionar_lotes_para_salida(
                lotes,
                float(cantidad_requerida)
            )

            return Response({
                'estrategia_usada': servicio.obtener_estrategia_actual(),
                'lotes_seleccionados': [
                    {
                        'lote_id': lote.id,
                        'producto': lote.producto_nombre,
                        'cantidad_a_usar': cantidad,
                        'numero_lote': lote.numero_lote,
                        'fecha_vencimiento': str(lote.fecha_vencimiento) if lote.fecha_vencimiento else None,
                        'dias_hasta_vencimiento': lote.dias_hasta_vencimiento,
                        'precio_compra': lote.precio_compra
                    }
                    for lote, cantidad in lotes_seleccionados
                ],
                'cantidad_total': sum(c for _, c in lotes_seleccionados)
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def _crear_lotes_ejemplo(producto: Producto) -> list:
        """
        Crea lotes de ejemplo para demostración.
        En producción, estos lotes vendrían de una tabla en la BD.
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