from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CitaViewSet, ServicioViewSet

# Un router crea automáticamente todas las URLs para un ViewSet
router = DefaultRouter()
router.register(r'citas', CitaViewSet, basename='cita')
router.register(r'servicios', ServicioViewSet, basename='servicio')

# Las URLs de la app son simplemente las que genera el router
urlpatterns = [
    path('', include(router.urls)),
]