"""
Usuario List Serializer - Listados optimizados de usuarios.
"""
from rest_framework import serializers
from usuarios.models import Usuario

class UsuarioListSerializer(serializers.ModelSerializer):
    """
    Serializer optimizado para listar usuarios en el sistema.
    
    Este serializer proporciona una vista simplificada de usuarios para listados,
    incluyendo información básica y roles, optimizado para rendimiento en
    colecciones grandes.
    
    Campos personalizados:
    - roles: Lista de nombres de roles (usando display names)
    - nombre_completo: Nombre y apellido concatenados
    
    Notas de implementación:
    - Usa select_related para optimizar queries de roles
    - Excluye campos innecesarios para listados (perfiles, timestamps)
    - Proporciona solo la información esencial para listados
    """
    
    roles = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nombre', 'apellido',
            'nombre_completo', 'estado', 'roles', 'created_at'
        ]
    
    def get_roles(self, obj):
        """Obtiene los roles del usuario."""
        return [ur.rol.get_nombre_display() for ur in obj.usuario_roles.select_related('rol')]
    
    def get_nombre_completo(self, obj):
        """Retorna el nombre completo."""
        return obj.get_full_name()
