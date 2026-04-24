"""
Perfil serializers - Serializer para el perfil del usuario autenticado.
"""
from rest_framework import serializers
from usuarios.models import Usuario, Cliente, Veterinario, Practicante
from usuarios.serializers.profiles import VeterinarioSerializer, PracticanteSerializer, ClienteSerializer

class UsuarioPerfilSerializer(serializers.ModelSerializer):
    """
    Serializer para ver/editar el perfil del usuario autenticado.

    Este serializer centraliza la información del usuario que ha iniciado sesión,
    incluyendo sus datos básicos, roles asignados y perfiles asociados
    (Veterinario, Practicante o Cliente).

    Características:
    - Combina datos del modelo Usuario con datos relacionados en modelos de perfil.
    - Permite actualización de perfiles anidados (cliente, veterinario, practicante).
    - Usa SerializerMethodField para lectura y serializers anidados para escritura.
    - Solo permite edición de campos limitados (controlado por `read_only_fields`).
    """
    
    # Campos dinámicos obtenidos mediante métodos personalizados (solo lectura)
    roles = serializers.SerializerMethodField()
    # Perfiles como serializers anidados para permitir escritura
    perfil_veterinario = VeterinarioSerializer(required=False, allow_null=True)
    perfil_practicante = PracticanteSerializer(required=False, allow_null=True)
    perfil_cliente = ClienteSerializer(required=False, allow_null=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nombre', 'apellido',
            'estado', 'roles', 'created_at',
            'perfil_veterinario', 'perfil_practicante', 'perfil_cliente'
        ]
        read_only_fields = ['id', 'username', 'created_at', 'estado']

    """ 
    --------------------------------------------
    MÉTODOS PERSONALIZADOS
    --------------------------------------------
    """
    
    def get_roles(self, obj):
        """Obtiene los roles del usuario."""
        return [ur.rol.get_nombre_display() for ur in obj.usuario_roles.select_related('rol')]
    
    def to_representation(self, instance):
        """
        Personaliza la representación para mostrar los perfiles correctamente.
        
        Convierte los perfiles de serializers anidados a diccionarios para la respuesta.
        """
        representation = super().to_representation(instance)
        
        # Reemplazar los perfiles con SerializerMethodField para lectura
        if hasattr(instance, 'perfil_veterinario'):
            representation['perfil_veterinario'] = VeterinarioSerializer(instance.perfil_veterinario).data
        else:
            representation['perfil_veterinario'] = None
            
        if hasattr(instance, 'perfil_practicante'):
            representation['perfil_practicante'] = PracticanteSerializer(instance.perfil_practicante).data
        else:
            representation['perfil_practicante'] = None
            
        if hasattr(instance, 'perfil_cliente'):
            representation['perfil_cliente'] = ClienteSerializer(instance.perfil_cliente).data
        else:
            representation['perfil_cliente'] = None
        
        return representation
    
    def update(self, instance, validated_data):
        """
        Actualiza el usuario y sus perfiles asociados.
        
        Maneja la actualización de:
        - Campos básicos del usuario (nombre, apellido, email)
        - Perfil de cliente (telefono, direccion)
        - Perfil de veterinario (licencia, especialidad, horario)
        - Perfil de practicante (tutor_veterinario, universidad, periodo_practica)
        """
        # Extraer datos de perfiles
        perfil_cliente_data = validated_data.pop('perfil_cliente', None)
        perfil_veterinario_data = validated_data.pop('perfil_veterinario', None)
        perfil_practicante_data = validated_data.pop('perfil_practicante', None)
        
        # Actualizar campos básicos del usuario
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar perfil de cliente si existe
        if perfil_cliente_data is not None:
            if hasattr(instance, 'perfil_cliente'):
                cliente = instance.perfil_cliente
                for attr, value in perfil_cliente_data.items():
                    setattr(cliente, attr, value)
                cliente.save()
            else:
                # Crear perfil de cliente si no existe
                Cliente.objects.create(usuario=instance, **perfil_cliente_data)
        
        # Actualizar perfil de veterinario si existe
        if perfil_veterinario_data is not None:
            if hasattr(instance, 'perfil_veterinario'):
                veterinario = instance.perfil_veterinario
                for attr, value in perfil_veterinario_data.items():
                    setattr(veterinario, attr, value)
                veterinario.save()
            else:
                # Crear perfil de veterinario si no existe
                Veterinario.objects.create(usuario=instance, **perfil_veterinario_data)
        
        # Actualizar perfil de practicante si existe
        if perfil_practicante_data is not None:
            if hasattr(instance, 'perfil_practicante'):
                practicante = instance.perfil_practicante
                for attr, value in perfil_practicante_data.items():
                    setattr(practicante, attr, value)
                practicante.save()
            else:
                # Crear perfil de practicante si no existe
                Practicante.objects.create(usuario=instance, **perfil_practicante_data)
        
        return instance
