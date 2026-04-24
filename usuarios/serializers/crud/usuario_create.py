"""
Usuario Create Serializer - Creación de usuarios con perfiles.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from usuarios.models import Veterinario, Practicante, Cliente, Usuario, Rol, UsuarioRol
from usuarios.serializers.profiles import VeterinarioSerializer, PracticanteSerializer, ClienteSerializer

class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación de usuarios."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    roles = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        write_only=True
    )
    
    # Campos de perfil según el rol
    perfil_veterinario = VeterinarioSerializer(required=False)
    perfil_practicante = PracticanteSerializer(required=False)
    perfil_cliente = ClienteSerializer(required=False)
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'nombre', 'apellido', 'estado', 'roles',
            'perfil_veterinario', 'perfil_practicante', 'perfil_cliente'
        ]
    
    def validate(self, attrs):
        """Validaciones personalizadas."""
        # Validar contraseñas coincidentes
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })
        
        # Validar roles existentes
        roles_input = attrs.get('roles', [])
        roles_validos = dict(Rol.ROLES_DISPONIBLES).keys()
        
        for rol_nombre in roles_input:
            if rol_nombre not in roles_validos:
                raise serializers.ValidationError({
                    'roles': f'El rol "{rol_nombre}" no es válido.'
                })
        
        # Validar que veterinarios tengan perfil
        if 'veterinario' in roles_input and 'perfil_veterinario' not in attrs:
            raise serializers.ValidationError({
                'perfil_veterinario': 'Los veterinarios deben tener perfil completo.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """
        Crea el usuario usando el Factory Method según el rol principal.
        """
        from usuarios.patterns.factory_method import UsuarioFactory
        roles = validated_data.pop('roles', [])
        password = validated_data.pop('password')
        validated_data.pop('password_confirm', None)

        # Extraer datos de perfiles
        perfil_veterinario_data = validated_data.pop('perfil_veterinario', None)
        perfil_practicante_data = validated_data.pop('perfil_practicante', None)
        perfil_cliente_data = validated_data.pop('perfil_cliente', None)

        # Determinar el tipo de usuario principal
        rol_principal = roles[0] if roles else 'cliente'
        factory = UsuarioFactory()
        usuario = factory.crear_usuario(rol_principal, validated_data)
        usuario.set_password(password)
        usuario.save()

        # Asignar roles adicionales si existen
        for rol_nombre in roles:
            rol_obj, _ = Rol.objects.get_or_create(nombre=rol_nombre)
            UsuarioRol.objects.create(usuario=usuario, rol=rol_obj)

        # Crear perfiles según el rol
        if perfil_veterinario_data:
            Veterinario.objects.create(usuario=usuario, **perfil_veterinario_data)
        if perfil_practicante_data:
            Practicante.objects.create(usuario=usuario, **perfil_practicante_data)
        if perfil_cliente_data:
            Cliente.objects.create(usuario=usuario, **perfil_cliente_data)

        return usuario
