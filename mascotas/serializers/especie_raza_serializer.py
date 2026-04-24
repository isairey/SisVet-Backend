from rest_framework import serializers
from mascotas.models import Especie, Raza


class EspecieCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar Especies.
    Permite escritura completa del campo nombre.
    """
    
    class Meta:
        model = Especie
        fields = ["id", "nombre"]
        read_only_fields = ["id"]
    
    def validate_nombre(self, value):
        """Valida que el nombre no esté vacío y lo normaliza."""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre de la especie no puede estar vacío.")
        return value.strip().title()


class RazaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar Razas.
    Permite especificar la especie por ID y valida la unicidad.
    """
    
    especie_nombre = serializers.CharField(source='especie.nombre', read_only=True)
    
    class Meta:
        model = Raza
        fields = ["id", "nombre", "especie", "especie_nombre"]
        read_only_fields = ["id", "especie_nombre"]
    
    def validate_nombre(self, value):
        """Valida que el nombre no esté vacío y lo normaliza."""
        if not value or not value.strip():
            raise serializers.ValidationError("El nombre de la raza no puede estar vacío.")
        return value.strip().title()
    
    def validate(self, data):
        """Valida que no exista una raza con el mismo nombre para la misma especie."""
        nombre = data.get('nombre')
        especie = data.get('especie')
        
        if nombre and especie:
            # Verificar si ya existe una raza con el mismo nombre para esta especie
            raza_existente = Raza.objects.filter(
                nombre__iexact=nombre,
                especie=especie
            ).exclude(id=self.instance.id if self.instance else None).first()
            
            if raza_existente:
                raise serializers.ValidationError(
                    f"Ya existe una raza llamada '{nombre}' para la especie '{especie.nombre}'."
                )
        
        return data

