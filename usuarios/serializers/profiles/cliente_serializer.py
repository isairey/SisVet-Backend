"""
Cliente Serializer - Serializer para el perfil de Cliente.
"""
from rest_framework import serializers
from usuarios.models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializer para el perfil de Cliente del sistema.

    Permite serializar la información complementaria del cliente,
    como su número telefónico y dirección.

    Es utilizado para mostrar o actualizar datos de contacto
    asociados a un usuario con rol 'cliente'.
    """
    
    class Meta:
        model = Cliente
        fields = ['telefono', 'direccion']
