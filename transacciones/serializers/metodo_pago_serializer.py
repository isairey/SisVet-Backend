from rest_framework import serializers
from transacciones.models.metodo_pago import MetodoPago

class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = '__all__'