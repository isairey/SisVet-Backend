"""
Configuración de URLs del módulo de Consultas.
Define las rutas de la API para el módulo de gestión de consultas y componentes relacionados.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.consulta_views import ConsultaViewSet
from .views.historia_clinica_views import HistoriaClinicaViewSet
from .views.prescripcion_views import PrescripcionViewSet
from .views.examen_views import ExamenViewSet
from .views.vacuna_views import HistorialVacunaViewSet
from .views.consentimiento_views import ConfirmarConsentimientoView


# Crear el router de Django REST Framework
router = DefaultRouter()

# Consultas: /api/consultas/
router.register(r'consultas', ConsultaViewSet, basename='consulta')

# Historias Clínicas: /api/historias-clinicas/
router.register(r'historias-clinicas', HistoriaClinicaViewSet, basename='historia-clinica')

# Prescripciones: /api/prescripciones/
# (Abarca la gestión de productos prescritos, antes "medicamentos")
router.register(r'prescripciones', PrescripcionViewSet, basename='prescripcion')

# Exámenes: /api/examenes/
router.register(r'examenes', ExamenViewSet, basename='examen')

# Vacunas: /api/vacunas/
router.register(r'vacunas', HistorialVacunaViewSet, basename='vacuna')

# Nombre de la app para namespacing
app_name = 'consultas'

# Patrones de URL
# IMPORTANTE: Las rutas personalizadas deben ir ANTES del router para evitar conflictos
urlpatterns = [
    # Ruta personalizada para confirmar consentimiento (debe ir antes del router)
    path('consultas/confirmar-consentimiento/', ConfirmarConsentimientoView.as_view(), name='confirmar-consentimiento'),
    # Incluir todas las rutas generadas automáticamente por el router
    path('', include(router.urls)),
]
