"""
Token serializers - Autenticación JWT personalizada.
"""
from rest_framework import serializers
from django.utils import timezone
from usuarios.models import Usuario
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed

# Jeronimo Rodriguez 10/31/2025 
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para la autenticación JWT.

    Este serializer amplía el comportamiento de `TokenObtainPairSerializer` 
    de SimpleJWT para incluir validaciones de seguridad adicionales y 
    proporcionar información personalizada del usuario dentro del token.
    
    - Extiende la funcionalidad del TokenObtainPairSerializer base de SimpleJWT.
    - Valida que el usuario esté activo y en estado 'activo' dentro del sistema.
    - Implementa control de seguridad ante múltiples intentos fallidos.
    - Incluye información adicional del usuario dentro del token (claims)
      y en la respuesta del login.
    """
    
    def validate(self, attrs):
        """
        Valida las credenciales del usuario y genera los tokens JWT usando Chain of Responsibility.
        Permite autenticación con username o email.
        """
        from usuarios.patterns.chain_of_responsibility import ValidadorCredenciales, ValidadorRol, ValidadorEstado
        username_or_email = attrs.get("username")
        password = attrs.get("password")

        # Buscar usuario por username o email
        user = self._obtener_usuario_por_username_o_email(username_or_email)
        
        if not user:
            raise serializers.ValidationError("Usuario o contraseña incorrectos.")

        # Verificar si el usuario está temporalmente bloqueado
        if user.esta_bloqueado():
            minutos_restantes = int((user.bloqueado_hasta - timezone.now()).total_seconds() // 60)
            raise serializers.ValidationError(
                f"Cuenta bloqueada temporalmente. Intente nuevamente en {minutos_restantes} minutos."
            )

        # Verificar estado del usuario ANTES de intentar la cadena de validadores
        if user.estado != 'activo':
            estado_display = user.get_estado_display() if hasattr(user, 'get_estado_display') else user.estado
            raise serializers.ValidationError(
                f'Esta cuenta está en estado: {estado_display}.'
            )

        # Verificar is_active después del estado personalizado
        if not user.is_active:
            raise serializers.ValidationError(
                'Esta cuenta está inactiva. Contacte al administrador.'
            )

        # Construir la cadena de validadores con el usuario ya encontrado
        cadena = ValidadorCredenciales(
            ValidadorRol(
                ValidadorEstado()
            )
        )
        request = {
            'user_obj': user,  # Pasar el usuario ya encontrado
            'password': password,
            'rol': user.usuario_roles.first().rol.nombre if user.usuario_roles.exists() else None,
            'estado': user.estado
        }
        
        # Validar credenciales y cadena de responsabilidad
        if not cadena.manejar(request):
            # Registrar intento fallido si la validación falla
            mensaje = user.registrar_intento_fallido()
            raise serializers.ValidationError(mensaje)

        # Actualizar attrs con el username real para que super().validate() funcione correctamente
        # Esto es necesario porque si el usuario ingresó email, attrs['username'] tiene el email
        attrs['username'] = user.username

        # Intentar autenticación normal (genera los tokens JWT)
        try:
            data = super().validate(attrs)
        except (serializers.ValidationError, AuthenticationFailed):
            mensaje = user.registrar_intento_fallido()
            raise serializers.ValidationError(mensaje)

        # Si la autenticación fue exitosa, reiniciar los intentos fallidos
        user.resetear_intentos()

        # Agregar información adicional del usuario a la respuesta
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'nombre_completo': self.user.get_full_name(),
            'roles': [ur.rol.nombre for ur in self.user.usuario_roles.select_related('rol')],
        }

        return data
    
    def _obtener_usuario_por_username_o_email(self, username_or_email):
        """
        Busca un usuario por username o email.
        
        Args:
            username_or_email: Puede ser username o email del usuario
            
        Returns:
            Usuario encontrado o None si no existe
        """
        try:
            # Intentar buscar por username primero
            return Usuario.objects.get(username=username_or_email)
        except Usuario.DoesNotExist:
            try:
                # Si no se encuentra por username, intentar por email
                return Usuario.objects.get(email=username_or_email)
            except Usuario.DoesNotExist:
                return None
    
    @classmethod
    def get_token(cls, user):
        """
        Sobrescribe la generación del token JWT para añadir 'claims' personalizados.
        Estos datos pueden ser leídos directamente desde el payload del token.
        """
        token = super().get_token(user)
        
        # Claims personalizados del usuario
        token['username'] = user.username
        token['email'] = user.email
        token['nombre'] = user.nombre
        token['apellido'] = user.apellido
        token['roles'] = [ur.rol.nombre for ur in user.usuario_roles.select_related('rol')]
        
        return token
