"""
Registro serializers - Manejo de registro con verificación en dos pasos.
"""
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from usuarios.models import Usuario, UsuarioPendiente, Rol, UsuarioRol, Cliente
from notificaciones.patterns.factory import NotificationFactory


class RegistroPendienteSerializer(serializers.ModelSerializer):
    """
    Serializer para registro inicial (Paso 1 de 2).
    
    Guarda TODOS los datos del usuario en UsuarioPendiente y envía
    el código de verificación por email.
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = UsuarioPendiente
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'nombre', 'apellido', 'telefono', 'direccion'
        ]
    
    def validate_username(self, value):
        """Valida que el username no esté ya registrado."""
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Este nombre de usuario ya está registrado.'
            )
        if UsuarioPendiente.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Este nombre de usuario ya está en proceso de verificación.'
            )
        return value
    
    def validate_email(self, value):
        """Valida que el email no esté ya registrado."""
        email_lower = value.lower()
        if Usuario.objects.filter(email=email_lower).exists():
            raise serializers.ValidationError(
                'Este correo electrónico ya está registrado.'
            )
        return email_lower
    
    def validate(self, attrs):
        """Valida que las contraseñas coincidan."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })
        return attrs
    
    def create(self, validated_data):
        """
        Crea o actualiza el UsuarioPendiente con todos los datos necesarios.
        Genera y envía el código de verificación por email.
        """
        # Extraer y procesar datos
        email = validated_data['email']
        password = make_password(validated_data.pop('password'))
        validated_data.pop('password_confirm')
        
        # Generar código de verificación de 6 dígitos
        verification_code = get_random_string(6, allowed_chars='0123456789')
        
        # Calcular tiempo de expiración (20 minutos desde ahora)
        code_expires_at = timezone.now() + timedelta(minutes=20)
        
        # Crear o actualizar usuario pendiente
        usuario_pendiente, _ = UsuarioPendiente.objects.update_or_create(
            email=email,
            defaults={
                **validated_data,
                'password': password,
                'verification_code': verification_code,
                'code_expires_at': code_expires_at,
                'intentos_verificacion': 0,  # Resetear intentos al regenerar código
            }
        )
        
        # Enviar código de verificación por email usando el patrón Factory
        # Usamos require_success=True para intentar envío síncrono con timeout
        # Si no se completa en 5s, el email se enviará en background
        try:
            notification_strategy = NotificationFactory.get_notification(
                evento="VERIFY_ACCOUNT_EMAIL",
                to_email=email,
                context={
                    "nombre": usuario_pendiente.nombre,
                    "code": verification_code
                }
            )
            # Intenta envío con timeout, si no se completa continúa en background
            notification_strategy.send(require_success=True)
        except Exception as e:
            # Solo lanzar error si hay un error real de configuración
            # Si es timeout, el email se enviará en background
            error_msg = f"Error al iniciar envío de email de verificación: {str(e)}"
            print(error_msg)
            # No bloquear el registro, el email se intentará enviar en background
            # El usuario puede usar "reenviar código" si no lo recibe
        
        return usuario_pendiente


class CodigoVerificacionSerializer(serializers.Serializer):
    """
    Serializer para verificación del código (Paso 2 de 2).
    
    Valida el código y completa el registro del usuario.
    """
    
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)
    
    def validate(self, attrs):
        """
        Valida el código de verificación y prepara los datos para
        la creación del Usuario definitivo.
        """
        email = attrs['email'].lower()
        code = attrs['code']
        
        # Buscar usuario pendiente
        try:
            usuario_pendiente = UsuarioPendiente.objects.get(email=email)
        except UsuarioPendiente.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'No existe un registro pendiente para este email.'
            })
        
        # Verificar límite de intentos
        if usuario_pendiente.max_intentos_excedidos:
            raise serializers.ValidationError(
                'Has excedido el número máximo de intentos. '
                'Solicita un nuevo código de verificación.'
            )
        
        # Verificar si el código expiró
        if not usuario_pendiente.es_codigo_valido():
            usuario_pendiente.incrementar_intentos()
            raise serializers.ValidationError({
                'code': 'El código ha expirado. Solicita uno nuevo.'
            })
        
        # Verificar el código
        if usuario_pendiente.verification_code != code:
            usuario_pendiente.incrementar_intentos()
            intentos_restantes = 5 - usuario_pendiente.intentos_verificacion
            raise serializers.ValidationError({
                'code': f'Código incorrecto. Intentos restantes: {intentos_restantes}'
            })
        
        # Guardar el usuario pendiente en validated_data para usarlo en la vista
        attrs['usuario_pendiente'] = usuario_pendiente
        return attrs


class ReenviarCodigoSerializer(serializers.Serializer):
    """
    Serializer para reenviar código de verificación.
    
    Permite reenviar el código incluso si el código anterior expiró (después de 20 minutos).
    Útil cuando:
    - El código expiró y el usuario necesita uno nuevo
    - El usuario no recibió el código original
    - El usuario quiere un nuevo código por seguridad
    """
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """
        Valida que exista un registro pendiente para este email.
        Permite reenviar incluso si el código anterior expiró.
        """
        email_lower = value.lower()
        try:
            usuario_pendiente = UsuarioPendiente.objects.get(email=email_lower)
            
            # Verificar que el usuario no haya excedido los intentos máximos
            # Si excedió, debe crear un nuevo registro
            if usuario_pendiente.max_intentos_excedidos:
                raise serializers.ValidationError(
                    'Has excedido el número máximo de intentos de verificación. '
                    'Por favor, realiza un nuevo registro.'
                )
            
            # Verificar que no exista ya un usuario activo con este email
            if Usuario.objects.filter(email=email_lower).exists():
                raise serializers.ValidationError(
                    'Este correo electrónico ya está registrado y verificado. '
                    'Si olvidaste tu contraseña, usa la opción de recuperación.'
                )
            
        except UsuarioPendiente.DoesNotExist:
            raise serializers.ValidationError(
                'No existe un registro pendiente para este email. '
                'Por favor, realiza el registro primero.'
            )
        return email_lower
    
    def save(self):
        """
        Regenera y reenvía el código de verificación.
        
        Esto funciona incluso si el código anterior expiró, permitiendo al usuario
        solicitar un nuevo código después de los 20 minutos.
        """
        email = self.validated_data['email']
        usuario_pendiente = UsuarioPendiente.objects.get(email=email)
        
        # Generar nuevo código de verificación
        verification_code = get_random_string(6, allowed_chars='0123456789')
        code_expires_at = timezone.now() + timedelta(minutes=20)
        
        # Actualizar usuario pendiente con nuevo código y resetear intentos
        usuario_pendiente.verification_code = verification_code
        usuario_pendiente.code_expires_at = code_expires_at
        usuario_pendiente.intentos_verificacion = 0  # Resetear intentos al generar nuevo código
        usuario_pendiente.save()
        
        # Reenviar email con el nuevo código
        # Usamos require_success=True para intentar envío síncrono con timeout
        try:
            notification_strategy = NotificationFactory.get_notification(
                evento="VERIFY_ACCOUNT_EMAIL",
                to_email=email,
                context={
                    "nombre": usuario_pendiente.nombre,
                    "code": verification_code
                }
            )
            # Intenta envío con timeout, si no se completa continúa en background
            notification_strategy.send(require_success=True)
        except Exception as e:
            # Solo lanzar error si hay un error real de configuración
            error_msg = f"Error al iniciar reenvío de email: {str(e)}"
            print(error_msg)
            # No bloquear, el email se intentará enviar en background
        
        return usuario_pendiente