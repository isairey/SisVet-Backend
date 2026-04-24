"""
Veterinario Serializer - Serializer para el perfil de Veterinario.
"""
from rest_framework import serializers
from usuarios.models import Veterinario

# Jerónimo Rodríguez - 30/10/2025
# Serializers de perfiles específicos del sistema
class VeterinarioSerializer(serializers.ModelSerializer):
    """
    Serializer para representar y validar los datos del perfil de un Veterinario.

    Este serializer se utiliza para mostrar o editar información
    complementaria de usuarios con rol 'veterinario'.
    
    Incluye validación personalizada del campo 'licencia' para garantizar
    que no existan duplicados en la base de datos.
    """
    
    class Meta:
        model = Veterinario
        fields = ['licencia', 'especialidad', 'horario']
    
    def validate_licencia(self, value):
        """
        Valida que el número de licencia veterinaria sea único en el sistema.

        - Permite mantener la licencia existente si el objeto ya está instanciado.
        - Lanza un ValidationError si el número de licencia ya se encuentra
          registrado en otro perfil.

        Retorna:
            str: valor validado de la licencia si no hay conflictos.
        """
        if self.instance and self.instance.licencia == value:
            return value
        
        if Veterinario.objects.filter(licencia=value).exists():
            raise serializers.ValidationError("Esta licencia ya está registrada.")
        return value
