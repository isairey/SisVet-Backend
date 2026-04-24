"""
Rol Serializer - Serializer para el modelo Rol.
"""
from rest_framework import serializers
from usuarios.models import Rol

# Jerónimo Rodríguez - 06/11/2025
# Serializers para el modelo Rol
class RolSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Rol."""
    
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion']
        read_only_fields = ['id']
