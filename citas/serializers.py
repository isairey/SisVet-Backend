from rest_framework import serializers
from django.utils import timezone
from .models import Servicio, Cita
from mascotas.models import Mascota
from usuarios.models import Usuario

class ServicioSerializer(serializers.ModelSerializer):
    """
    Capa de Presentación: Traduce el modelo Servicio a JSON.
    """
    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'costo']

class CitaSerializer(serializers.ModelSerializer):
    """
    Serializer para LEER (GET) una Cita. Muestra los nombres.
    """
    mascota_nombre = serializers.CharField(source='mascota.nombre', read_only=True)
    veterinario_nombre = serializers.CharField(source='veterinario.get_full_name', read_only=True)
    servicio_nombre = serializers.CharField(source='servicio.nombre', read_only=True)
    estado = serializers.CharField(source='get_estado_display', read_only=True) # Muestra "Agendada"

    class Meta:
        model = Cita
        fields = [
            'id', 'mascota_nombre', 'veterinario_nombre', 'servicio_nombre',
            'fecha_hora', 'estado'
        ]
        read_only_fields = fields # Este serializer es solo para LEER


class CrearCitaSerializer(serializers.Serializer):
    """
    Serializer para CREAR (POST) una Cita.
    Espera recibir solo los IDs (UUIDs) del frontend.
    """
    mascota_id = serializers.UUIDField(required=True)
    veterinario_id = serializers.UUIDField(required=True)
    servicio_id = serializers.UUIDField(required=True)
    fecha_hora = serializers.DateTimeField(required=True)
    observaciones = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_fecha_hora(self, value):
        """Valida que la fecha no sea en el pasado."""
        if value < timezone.now():
            raise serializers.ValidationError("No se pueden agendar citas en el pasado.")
        return value

class ReagendarCitaSerializer(serializers.Serializer):
    """Serializer solo para la acción de reagendar."""
    fecha_hora = serializers.DateTimeField(required=True)

    def validate_fecha_hora(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("No se pueden reagendar citas al pasado.")
        return value