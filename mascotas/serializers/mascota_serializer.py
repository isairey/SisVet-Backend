from rest_framework import serializers
from mascotas.models import Mascota, Especie, Raza
from usuarios.models import Cliente

# Jeronimo Rodriguez - 11/03/2025

class EspecieSerializer(serializers.ModelSerializer):
    """Serializer para listar o crear Especie.

    Campos principales:
    - id: UUID (read-only)
    - nombre: nombre de la especie (string)
    """

    class Meta:
        model = Especie
        fields = ["id", "nombre"]


class RazaSerializer(serializers.ModelSerializer):
    """Serializer para listar o crear Raza.

    Devuelve además la `especie` relacionada en forma anidada (solo lectura).
    """

    especie = EspecieSerializer(read_only=True)

    class Meta:
        model = Raza
        fields = ["id", "nombre", "especie"]


class MascotaSerializer(serializers.ModelSerializer):
    """Serializer principal de Mascota para operaciones CRUD.

    - En entrada (create/update) acepta relaciones por su ID (cliente es read-only
      y se asigna automáticamente al usuario autenticado).
    - En salida (representación) devuelve nombres legibles para las relaciones
      `cliente`, `especie` y `raza`.
    """

    cliente = serializers.PrimaryKeyRelatedField(read_only=True)
    # Permitir que especie/raza sean nulos al crear/editar
    especie = serializers.PrimaryKeyRelatedField(queryset=Especie.objects.all(), allow_null=True, required=False)
    raza = serializers.PrimaryKeyRelatedField(queryset=Raza.objects.all(), allow_null=True, required=False)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Mascota
        fields = [
            'id', 'cliente', 'nombre', 'sexo', 'especie', 'raza',
            'fecha_nacimiento', 'peso', 'created_at'
        ]
        read_only_fields = ("id", "cliente", "created_at")

    def create(self, validated_data):
        """Crea una Mascota y la asocia al perfil `Cliente` del usuario autenticado.

        Lanza `serializers.ValidationError` si el usuario autenticado no tiene perfil
        `Cliente` asociado.
        """

        request = self.context.get("request")
        try:
            cliente = Cliente.objects.get(usuario=request.user)
        except Cliente.DoesNotExist:
            raise serializers.ValidationError("El usuario autenticado no tiene perfil de cliente.")

        validated_data["cliente"] = cliente
        mascota = Mascota.objects.create(**validated_data)
        return mascota

    def to_representation(self, instancia):
        """Construye la representación JSON de salida.

        - Reemplaza los IDs de relaciones por valores legibles:
          `cliente` -> nombre completo del propietario
          `especie`  -> nombre de la especie
          `raza`     -> nombre de la raza
        - Mantiene la serialización estándar para el resto de campos.
        """

        salida = super().to_representation(instancia)

        # Cliente: mostrar nombre completo si existe el perfil
        try:
            salida["cliente"] = instancia.cliente.usuario.get_full_name() if instancia.cliente else None
        except Exception:
            # Fallback si por alguna razón la relación no está disponible
            salida["cliente"] = None

        # Especie: mostrar nombre o None
        salida["especie"] = instancia.especie.nombre if getattr(instancia, "especie", None) else None

        # Raza: mostrar nombre o None
        salida["raza"] = instancia.raza.nombre if getattr(instancia, "raza", None) else None

        return salida