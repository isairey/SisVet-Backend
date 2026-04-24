"""
Cambiar Password Serializer - Cambio de contraseña de usuarios.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

class CambiarPasswordSerializer(serializers.Serializer):
    """
    Serializer para cambio de contraseña.
    
    Este serializer valida el cambio de contraseña considerando dos casos:
    1. Usuario cambiando su propia contraseña: valida password_actual contra request.user
    2. Administrador cambiando contraseña de otro usuario: valida password_actual contra 
       el usuario objetivo (pasado en el contexto)
    """
    
    password_actual = serializers.CharField(required=True, write_only=True)
    password_nueva = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    password_nueva_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Validar contraseñas."""
        if attrs['password_nueva'] != attrs['password_nueva_confirm']:
            raise serializers.ValidationError({
                'password_nueva_confirm': 'Las contraseñas no coinciden.'
            })
        return attrs
    
    def validate_password_actual(self, value):
        """
        Validar que la contraseña actual sea correcta.
        
        Siempre valida contra request.user (el usuario autenticado):
        - Si el usuario cambia su propia contraseña: valida su propia contraseña
        - Si un administrador cambia la contraseña de otro usuario: valida la contraseña del administrador
        """
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError('Usuario no autenticado.')
        
        # Siempre validar contra el usuario autenticado (request.user)
        # Esto asegura que:
        # 1. Un usuario debe proporcionar su propia contraseña para cambiar su contraseña
        # 2. Un administrador debe proporcionar su propia contraseña para cambiar la contraseña de otro usuario
        user = request.user
        if not user.check_password(value):
            raise serializers.ValidationError('La contraseña actual es incorrecta.')
        return value
