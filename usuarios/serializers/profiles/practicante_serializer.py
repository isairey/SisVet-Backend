"""
Practicante Serializer - Serializer para el perfil de Practicante.
"""
from rest_framework import serializers
from usuarios.models import Practicante

class PracticanteSerializer(serializers.ModelSerializer):
    """
    Serializer para el perfil de un usuario con rol 'practicante'.

    Incluye la información del tutor veterinario asignado, universidad
    de procedencia y el período de práctica profesional.

    El campo `tutor_veterinario_nombre` se obtiene dinámicamente mediante
    `SerializerMethodField` para mostrar el nombre legible del tutor.
    """
    
    tutor_veterinario_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Practicante
        fields = ['tutor_veterinario', 'tutor_veterinario_nombre', 'universidad', 'periodo_practica']
    
    def get_tutor_veterinario_nombre(self, obj):
        """
        Retorna el nombre completo del tutor veterinario si existe.

        Si el practicante no tiene tutor asignado, retorna `None`.

        Args:
            obj (Practicante): instancia del modelo Practicante.
        Returns:
            str | None: nombre del tutor o None si no existe.
        """
        if obj.tutor_veterinario:
            return str(obj.tutor_veterinario)
        return None
