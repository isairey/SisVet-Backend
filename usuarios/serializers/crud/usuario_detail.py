"""
Usuario Detail Serializer - Detalles completos de usuarios.
"""
from rest_framework import serializers
from usuarios.models import Usuario
from usuarios.serializers.profiles import VeterinarioSerializer, PracticanteSerializer, ClienteSerializer, RolSerializer

class UsuarioDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo para mostrar todos los detalles de un usuario.
    
    Este serializer incluye toda la información disponible de un usuario,
    incluyendo sus perfiles específicos (veterinario, practicante, cliente)
    y sus roles asignados.
    
    Características:
    - Incluye timestamps de auditoría (created_at, updated_at)
    - Expone todos los perfiles asociados como read-only
    - Proporciona información detallada de roles
    
    Notas de implementación:
    - Los perfiles son read_only para prevenir modificación directa
    - Los campos de auditoría y el ID son read_only por seguridad
    - Utiliza RolSerializer para información detallada de roles
    """
    
    roles = serializers.SerializerMethodField()
    perfil_veterinario = VeterinarioSerializer(read_only=True)
    perfil_practicante = PracticanteSerializer(read_only=True)
    perfil_cliente = ClienteSerializer(read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nombre', 'apellido',
            'estado', 'roles', 'created_at', 'updated_at',
            'perfil_veterinario', 'perfil_practicante', 'perfil_cliente'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_roles(self, obj):
        """Obtiene información detallada de los roles."""
        return RolSerializer(
            [ur.rol for ur in obj.usuario_roles.select_related('rol')],
            many=True
        ).data
