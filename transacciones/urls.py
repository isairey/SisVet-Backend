from django.urls import path
from transacciones.views.factura_view import (
    FacturaListCreateView,
    FacturaDetailView
)
from transacciones.views.pago_view import PagoListCreateView
from transacciones.views.metodo_pago_view import MetodoPagoListView, MetodoPagoDetailView
from transacciones.views.crear_factura_actions import (
    CrearFacturaDesdeCita,
    CrearFacturaDesdeConsulta
)
from transacciones.views.factura_producto_view import CrearFacturaDesdeProductosView
from transacciones.views.factura_actions import (
    PagarFacturaView,
    AnularFacturaView,
    EnviarFacturaEmailView
)
from transacciones.views.reportes_view import ReportesFinancierosView
from transacciones.views.recibo_view import ReciboFacturaView

urlpatterns = [

    # Facturas
    path('facturas/', FacturaListCreateView.as_view(), name='factura-list-create'),
    path('facturas/<int:pk>/', FacturaDetailView.as_view(), name='factura-detail'),

    # Acciones especiales
    path("facturas/crear-desde-cita/<int:cita_id>/", CrearFacturaDesdeCita.as_view()),
    path("facturas/crear-desde-consulta/<int:consulta_id>/", CrearFacturaDesdeConsulta.as_view()),
    path("facturas/crear-desde-productos/", CrearFacturaDesdeProductosView.as_view(), name='factura-desde-productos'),

    # Envio de factura de forma manual por solicitud
    path("facturas/<int:factura_id>/enviar-email/", EnviarFacturaEmailView.as_view()),

    # Acciones de pagos
    path('facturas/<int:factura_id>/pagar/', PagarFacturaView.as_view()),
    path('facturas/<int:factura_id>/anular/', AnularFacturaView.as_view()),

    # Recibos
    path('facturas/<int:factura_id>/recibo/', ReciboFacturaView.as_view(), name='factura-recibo'),

    # Reportes financieros
    path('reportes-financieros/', ReportesFinancierosView.as_view(), name='reportes-financieros'),

    # Pagos
    path('pagos/', PagoListCreateView.as_view(), name='pago-list-create'),

    # Métodos de pago
    path('metodos-pago/', MetodoPagoListView.as_view(), name='metodo-pago-list'),
    path('metodos-pago/<int:pk>/', MetodoPagoDetailView.as_view(), name='metodo-pago-detail'),
]