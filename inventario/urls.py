from django.urls import path, include
from rest_framework.routers import DefaultRouter

from django.contrib import admin
from .views import MarcaViewSet, CategoriaViewSet, ProductoViewSet, KardexViewSet, NotificacionViewSet
from .views.lote_view import LoteViewSet

router = DefaultRouter()
router.register(r"marcas", MarcaViewSet)
router.register(r"categorias", CategoriaViewSet)
router.register(r"productos", ProductoViewSet)
router.register(r'kardex', KardexViewSet)
router.register(r'notificaciones', NotificacionViewSet)
router.register(r'lotes', LoteViewSet, basename='lote')

urlpatterns = router.urls

