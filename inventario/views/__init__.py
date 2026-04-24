"""
inventario/views/__init__.py

Importa todos los ViewSets para facilitar su uso.
"""
from .marca_views import MarcaViewSet
from .categoria_views import CategoriaViewSet
from .producto_views import ProductoViewSet
from .kardex_views import KardexViewSet
from .notificacion_views import NotificacionViewSet

# ✨ OPCIONAL: También puedes importar las views admin aquí
# from .inventario_admin_views import (
#     ajustar_stock_manual,
#     conteo_fisico,
#     consultar_stock_producto,
#     historial_operaciones,
# )

__all__ = [
    'MarcaViewSet',
    'CategoriaViewSet',
    'ProductoViewSet',
    'KardexViewSet',
    'NotificacionViewSet',
]