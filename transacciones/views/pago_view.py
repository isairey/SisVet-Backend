from rest_framework import generics
from transacciones.models.pago import Pago
from transacciones.serializers.pago_serializer import PagoSerializer


class PagoListCreateView(generics.ListCreateAPIView):
    queryset = Pago.objects.all().select_related('factura', 'metodo_pago')
    serializer_class = PagoSerializer