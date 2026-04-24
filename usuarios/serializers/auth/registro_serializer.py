"""
Registro serializers - Auto-registro de usuarios.
"""
from rest_framework import serializers
from usuarios.models import Usuario, Rol, UsuarioRol, Cliente

# Jeronimo Rodriguez 10/30/2025 
class RegistroSerializer(serializers.ModelSerializer):
    """Serializer para auto-registro de clientes (público).
    Maneja:
    - Validación básica de contraseñas (coincidencia).
    - Creación del objeto Usuario usando el manager personalizado.
    - Asignación del rol 'cliente' y creación del perfil Cliente asociado.
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
    # Campos opcionales del perfil de cliente (no forman parte del modelo Usuario)
    telefono = serializers.CharField(required=False, allow_blank=True)
    direccion = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'nombre', 'apellido', 'telefono', 'direccion'
        ]
    
    def validate(self, attrs):

        """Validaciones de entrada antes de crear el usuario.

        Actualmente verifica que `password` y `password_confirm` coincidan.
        Levanta ValidationError con un mensaje claro en caso de discrepancia.
        """

        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })
        return attrs
    
    def create(self, validated_data):
        """Crea un Usuario con rol 'cliente' y su perfil Cliente.

        Flujo:
        1. Extrae y elimina campos de perfil (teléfono, dirección) y password_confirm.
        2. Crea el Usuario usando `create_user` del manager (asegura hashing).
        3. Asigna (o crea si no existe) el Rol 'cliente' y la relación UsuarioRol.
        4. Crea el perfil Cliente vinculado al usuario.

        Retorna el objeto Usuario creado.
        """
        
        # Extraer datos de perfil que no pertenecen al modelo Usuario
        telefono = validated_data.pop('telefono', '')
        direccion = validated_data.pop('direccion', '')
        # Quitar campo auxiliar de confirmación de contraseña
        validated_data.pop('password_confirm')
        
        # Crear usuario (manager debe encargarse del hashing de la contraseña)
        password = validated_data.pop('password')
        usuario = Usuario.objects.create_user(password=password, **validated_data)
        
        # Asignar rol de cliente (se crea si no existe)
        rol_cliente, _ = Rol.objects.get_or_create(nombre='cliente')
        UsuarioRol.objects.create(usuario=usuario, rol=rol_cliente)
        
        # Crear perfil de cliente con los datos opcionales
        Cliente.objects.create(
            usuario=usuario,
            telefono=telefono,
            direccion=direccion
        )
        
        return usuario
