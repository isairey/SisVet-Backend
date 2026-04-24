# apps/consultas/serializers/examen_serializers.py

"""
Serializers para el modelo Examen.
"""

from rest_framework import serializers
from consultas.models import Examen


class ExamenSerializer(serializers.ModelSerializer):
    """
    Serializer para exámenes médicos ordenados.
    """

    tipo_examen_display = serializers.CharField(
        source='get_tipo_examen_display',
        read_only=True,
        help_text="Nombre legible del tipo de examen"
    )

    class Meta:
        model = Examen
        fields = [
            'id',
            'consulta',
            'tipo_examen',
            'tipo_examen_display',
            'descripcion',
            'fecha_orden',
        ]
        read_only_fields = ['id', 'fecha_orden']


class ExamenCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear exámenes (usado en nested create).
    """
    class Meta:
        model = Examen
        fields = [
            'tipo_examen',
            'descripcion',
        ]