"""
Usuario Update Serializer - Actualización de usuarios y perfiles.
"""
from rest_framework import serializers
from usuarios.models import Usuario, Cliente, Veterinario, Practicante
from usuarios.serializers.profiles import VeterinarioSerializer, PracticanteSerializer, ClienteSerializer

class UsuarioUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualización de usuarios."""
    
    perfil_veterinario = VeterinarioSerializer(required=False)
    perfil_practicante = PracticanteSerializer(required=False)
    perfil_cliente = ClienteSerializer(required=False)
    
    class Meta:
        model = Usuario
        fields = [
            'email', 'nombre', 'apellido', 'estado',
            'perfil_veterinario', 'perfil_practicante', 'perfil_cliente'
        ]
    
    def to_internal_value(self, data):
        """
        Sobrescribe to_internal_value para pasar la instancia correcta
        a los serializers anidados durante la validación.
        
        Esto permite que la validación de la licencia en VeterinarioSerializer
        funcione correctamente al tener acceso a la instancia existente.
        """
        # Extraer los datos de perfiles antes de la validación automática
        # Usar get() en lugar de pop() para no modificar el diccionario original
        perfil_veterinario_data = data.get('perfil_veterinario')
        perfil_practicante_data = data.get('perfil_practicante')
        perfil_cliente_data = data.get('perfil_cliente')
        
        # Crear una copia de data sin los perfiles para la validación del padre
        data_sin_perfiles = {k: v for k, v in data.items() 
                            if k not in ['perfil_veterinario', 'perfil_practicante', 'perfil_cliente']}
        
        # Obtener el valor interno del serializer padre (sin los perfiles)
        ret = super().to_internal_value(data_sin_perfiles)
        
        # Validar los perfiles con la instancia correcta si existe
        if self.instance:
            # Validar perfil de veterinario
            if perfil_veterinario_data is not None and hasattr(self.instance, 'perfil_veterinario'):
                veterinario_serializer = VeterinarioSerializer(
                    instance=self.instance.perfil_veterinario,
                    data=perfil_veterinario_data,
                    partial=True
                )
                veterinario_serializer.is_valid(raise_exception=True)
                ret['perfil_veterinario'] = veterinario_serializer.validated_data
            elif perfil_veterinario_data is not None:
                # Si se envía pero no existe el perfil, validar sin instancia (creación)
                veterinario_serializer = VeterinarioSerializer(data=perfil_veterinario_data)
                veterinario_serializer.is_valid(raise_exception=True)
                ret['perfil_veterinario'] = veterinario_serializer.validated_data
            
            # Validar perfil de practicante
            if perfil_practicante_data is not None and hasattr(self.instance, 'perfil_practicante'):
                practicante_serializer = PracticanteSerializer(
                    instance=self.instance.perfil_practicante,
                    data=perfil_practicante_data,
                    partial=True
                )
                practicante_serializer.is_valid(raise_exception=True)
                ret['perfil_practicante'] = practicante_serializer.validated_data
            elif perfil_practicante_data is not None:
                practicante_serializer = PracticanteSerializer(data=perfil_practicante_data)
                practicante_serializer.is_valid(raise_exception=True)
                ret['perfil_practicante'] = practicante_serializer.validated_data
            
            # Validar perfil de cliente
            if perfil_cliente_data is not None and hasattr(self.instance, 'perfil_cliente'):
                cliente_serializer = ClienteSerializer(
                    instance=self.instance.perfil_cliente,
                    data=perfil_cliente_data,
                    partial=True
                )
                cliente_serializer.is_valid(raise_exception=True)
                ret['perfil_cliente'] = cliente_serializer.validated_data
            elif perfil_cliente_data is not None:
                cliente_serializer = ClienteSerializer(data=perfil_cliente_data)
                cliente_serializer.is_valid(raise_exception=True)
                ret['perfil_cliente'] = cliente_serializer.validated_data
        
        return ret
    
    def update(self, instance, validated_data):
        """Actualiza el usuario y sus perfiles."""
        # Extraer datos de perfiles
        perfil_veterinario_data = validated_data.pop('perfil_veterinario', None)
        perfil_practicante_data = validated_data.pop('perfil_practicante', None)
        perfil_cliente_data = validated_data.pop('perfil_cliente', None)
        
        # Actualizar usuario
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar perfiles
        if perfil_veterinario_data is not None and hasattr(instance, 'perfil_veterinario'):
            for attr, value in perfil_veterinario_data.items():
                setattr(instance.perfil_veterinario, attr, value)
            instance.perfil_veterinario.save()
        
        if perfil_practicante_data is not None and hasattr(instance, 'perfil_practicante'):
            for attr, value in perfil_practicante_data.items():
                setattr(instance.perfil_practicante, attr, value)
            instance.perfil_practicante.save()
        
        if perfil_cliente_data is not None and hasattr(instance, 'perfil_cliente'):
            for attr, value in perfil_cliente_data.items():
                setattr(instance.perfil_cliente, attr, value)
            instance.perfil_cliente.save()
        
        return instance
