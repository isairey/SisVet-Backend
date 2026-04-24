from rest_framework import serializers
from django.utils import timezone
from citas.models import Cita, Servicio

class CrearCitaSerializer(serializers.Serializer):
    """
    Solo valida los datos de entrada. 
    """
    mascota_id = serializers.IntegerField(required=True)
    veterinario_id = serializers.IntegerField(required=True)
    servicio_id = serializers.IntegerField(required=True)
    fecha_hora = serializers.DateTimeField(required=True)
    observaciones = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_fecha_hora(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("No se pueden agendar citas en el pasado.")
        return value

class ReagendarCitaSerializer(serializers.Serializer):
    """
    Solo valida el nuevo horario.
    """
    fecha_hora = serializers.DateTimeField(required=True)

    def validate_fecha_hora(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("No se pueden reagendar citas al pasado.")
        return value

class ServicioWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ['nombre', 'costo']
