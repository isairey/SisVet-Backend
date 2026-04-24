# Estos serializers solo se usan para mostrar datos (GET). Son los "traductores" de Python a JSON.
from rest_framework import serializers
from ..models import Servicio, Cita

class ServicioSerializer(serializers.ModelSerializer):
    """Serializer para LEER (GET) los Servicios."""
    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'costo']


class CitaSerializer(serializers.ModelSerializer):
    """
    Serializer para LEER (GET) una Cita.
    Muestra nombres (ej. "Max") en lugar de solo IDs .
    """
    mascota_nombre = serializers.CharField(source='mascota.nombre', read_only=True)
    veterinario_nombre = serializers.CharField(source='veterinario.get_full_name', read_only=True)
    servicio_nombre = serializers.CharField(source='servicio.nombre', read_only=True)

    class Meta:
        model = Cita
        fields = [
            'id', 
            'mascota', # ID de la mascota
            'veterinario', # ID del veterinario
            'servicio', # ID del servicio
            'mascota_nombre', 
            'veterinario_nombre', 
            'servicio_nombre', 
            'fecha_hora', 
            'estado',
            'observaciones'
        ]
        # Hacemos todos los campos de solo lectura por seguridad,
        # ya que este serializer NUNCA debe usarse para escribir.
        read_only_fields = fields