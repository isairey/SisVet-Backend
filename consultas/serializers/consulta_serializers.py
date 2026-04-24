"""
Serializers para el modelo Consulta.
Representa el formulario completo "Crear Historias Clínicas".
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from consultas.models import Consulta
from mascotas.models import Mascota

from .prescripcion_serializers import (
    PrescripcionSerializer,
    PrescripcionCreateSerializer
)
from .examen_serializers import ExamenSerializer, ExamenCreateSerializer
from .vacuna_serializers import HistorialVacunaSerializer, HistorialVacunaCreateSerializer


User = get_user_model()
VETERINARIO_GET = 'veterinario.get_full_name'


# SERIALIZER - LISTADO
class ConsultaListSerializer(serializers.ModelSerializer):
    mascota_nombre = serializers.CharField(source='mascota.nombre', read_only=True)
    veterinario_nombre = serializers.CharField(source=VETERINARIO_GET, read_only=True)
    estado_vacunacion = serializers.SerializerMethodField()
    total_prescripciones = serializers.SerializerMethodField()

    class Meta:
        model = Consulta
        fields = [
            'id',
            'mascota_nombre',
            'veterinario_nombre',
            'fecha_consulta',
            'diagnostico',
            'estado_vacunacion',
            'total_prescripciones',
        ]

    def get_estado_vacunacion(self, obj):
        return obj.get_estado_vacunacion_consulta()

    def get_total_prescripciones(self, obj):
        return obj.get_prescripciones_count()

# SERIALIZER - DETALLE
class ConsultaDetailSerializer(serializers.ModelSerializer):
    datos_personales = serializers.SerializerMethodField()
    veterinario_nombre = serializers.CharField(source=VETERINARIO_GET, read_only=True)

    prescripciones = PrescripcionSerializer(many=True, read_only=True)
    examenes = ExamenSerializer(many=True, read_only=True)
    vacunas = HistorialVacunaSerializer(many=True, read_only=True)

    class Meta:
        model = Consulta
        fields = [
            'id',
            'mascota',
            'datos_personales',
            'veterinario',
            'veterinario_nombre',
            'fecha_consulta',
            'descripcion_consulta',
            'diagnostico',
            'notas_adicionales',
            'prescripciones',
            'examenes',
            'vacunas',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_datos_personales(self, obj):
        mascota = obj.mascota
        cliente = getattr(mascota, "cliente", None)

        if not cliente:
            return None

        return {
            "nombre": f"{cliente.usuario.nombre} {cliente.usuario.apellido}",
            "telefono": getattr(cliente, "telefono", None),
            "direccion": getattr(cliente, "direccion", None),
        }

# SERIALIZER - CREAR CONSULTA COMPLETA
class ConsultaCreateSerializer(serializers.ModelSerializer):
    prescripciones = PrescripcionCreateSerializer(many=True, required=False)
    examenes = ExamenCreateSerializer(many=True, required=False)
    vacunas = HistorialVacunaCreateSerializer(required=False)

    class Meta:
        model = Consulta
        fields = [
            'servicio',
            'cita',
            'mascota',
            'veterinario',
            'fecha_consulta',
            'descripcion_consulta',
            'diagnostico',
            'notas_adicionales',
            'prescripciones',
            'examenes',
            'vacunas',
        ]

    # VALIDACIONES BÁSICAS
    def validate_mascota(self, value):
        if not Mascota.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("La mascota seleccionada no existe")
        return value

    def validate_descripcion_consulta(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("La descripción de la consulta es obligatoria")
        return value

    def validate_diagnostico(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("Debe ingresar un diagnóstico")
        return value

    # ---------------------
    # CREACIÓN - DELEGADA A SERVICES
    # ---------------------
    def create(self, validated_data):
        from consultas.services.consulta_service import crear_consulta_completa
        return crear_consulta_completa(validated_data)

    def to_representation(self, instance):
        return ConsultaDetailSerializer(instance, context=self.context).data

# SERIALIZER GENERAL
class ConsultaSerializer(serializers.ModelSerializer):
    mascota_nombre = serializers.CharField(source='mascota.nombre', read_only=True)
    veterinario_nombre = serializers.CharField(source=VETERINARIO_GET, read_only=True)

    class Meta:
        model = Consulta
        fields = [
            'id',
            'mascota',
            'mascota_nombre',
            'veterinario',
            'veterinario_nombre',
            'fecha_consulta',
            'descripcion_consulta',
            'diagnostico',
            'notas_adicionales',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ConsultaUpdateSerializer(ConsultaCreateSerializer):
    """
    Permite la actualización completa reutilizando las validaciones de creación.
    """
    class Meta(ConsultaCreateSerializer.Meta):
        model = Consulta
        # Aseguramos que se usen los mismos campos que en la creación
        fields = ConsultaCreateSerializer.Meta.fields
        from consultas.models import Prescripcion, Examen, HistorialVacuna as Vacuna

    def update(self, instance, validated_data):
        from consultas.services.consulta_service import actualizar_consulta_completa
        try:
            return actualizar_consulta_completa(instance, validated_data)
        except Exception as e:
            print(f"❌ ERROR EN UPDATE: {e}")
            import traceback
            traceback.print_exc()
            raise serializers.ValidationError({"detail": str(e)})