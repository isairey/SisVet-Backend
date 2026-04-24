from django.urls import path
from mascotas.views.mascota_views import (
    MascotaListCreateView,
    MascotaRetrieveUpdateDeleteView,
    EspecieListCreateView,
    RazaListCreateView,
)

# Jeronimo Rodriguez - 11/03/2025

urlpatterns = [
    path('mascotas/especies/', EspecieListCreateView.as_view(), name='especies-list-create'),
    path('mascotas/razas/', RazaListCreateView.as_view(), name='razas-list-create'),
    path('mascotas/', MascotaListCreateView.as_view(), name='mascotas-list-create'),
    # Use integer primary keys (BaseModel.id es BigAutoField en este proyecto).
    path('mascotas/<int:pk>/', MascotaRetrieveUpdateDeleteView.as_view(), name='mascota-detail'),
]