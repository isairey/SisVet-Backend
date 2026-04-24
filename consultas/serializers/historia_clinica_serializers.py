# apps/consultas/serializers/historia_clinica_serializers.py

"""
Serializers para el modelo HistoriaClinica.
Implementa el COMPOSITE PATTERN.
"""

from rest_framework import serializers
from django.db.models import Count
# IMPORTANTE: Usar el modelo de consultas, NO de mascotas
from consultas.models import HistoriaClinica
from mascotas.models import Mascota
from .consulta_serializers import ConsultaDetailSerializer
from consultas.services.historia_service import (
    obtener_estadisticas_historia,
    obtener_medicamentos_frecuentes,
    obtener_ultima_consulta,
)


class HistoriaClinicaSerializer(serializers.ModelSerializer):
    """
    Serializer básico para Historia Clínica.
    """
    mascota = serializers.SerializerMethodField()
    propietario_nombre = serializers.CharField(
        source='mascota.cliente.usuario.get_full_name',
        read_only=True
    )
    estado_vacunacion_display = serializers.CharField(
        source='get_estado_vacunacion_actual_display',
        read_only=True
    )
    total_consultas = serializers.SerializerMethodField()
    ultima_consulta_fecha = serializers.SerializerMethodField()

    class Meta:
        model = HistoriaClinica
        fields = [
            'id',
            'mascota',
            'propietario_nombre',
            'fecha_creacion',
            'fecha_actualizacion',
            'estado_vacunacion_actual',
            'estado_vacunacion_display',
            'total_consultas',
            'ultima_consulta_fecha',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def get_mascota(self, obj):
        """Retorna datos básicos de la mascota como objeto"""
        mascota = obj.mascota
        return {
            'id': str(mascota.id),
            'nombre': mascota.nombre,
            'especie': mascota.especie.nombre if mascota.especie else None,
            'raza': mascota.raza.nombre if mascota.raza else None,
        }

    def get_total_consultas(self, obj):
        """Retorna el número total de consultas"""
        return obj.get_total_consultas()

    def get_ultima_consulta_fecha(self, obj):
        """Retorna la fecha de la última consulta"""
        ultima = obj.mascota.consultas.order_by('-fecha_consulta').first()
        return ultima.fecha_consulta if ultima else None


class HistoriaClinicaDetalleSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para Historia Clínica consolidada.
    """
    # Datos de la mascota (Composite root)
    mascota_datos = serializers.SerializerMethodField(help_text="Datos completos de la mascota")
    # Propietario
    propietario = serializers.SerializerMethodField(help_text="Datos del propietario de la mascota")
    # Lista de consultas (Components)
    consultas = serializers.SerializerMethodField(help_text="Todas las consultas ordenadas cronológicamente (más recientes primero)")
    # Estadísticas generales
    estadisticas = serializers.SerializerMethodField(help_text="Estadísticas generales de la historia clínica")
    # Medicamentos más frecuentes
    medicamentos_frecuentes = serializers.SerializerMethodField(help_text="Top 5 medicamentos más prescritos")

    class Meta:
        model = HistoriaClinica
        fields = [
            'id',
            'mascota',
            'mascota_datos',
            'propietario',
            'fecha_creacion',
            'fecha_actualizacion',
            'estado_vacunacion_actual',
            'consultas',
            'estadisticas',
            'medicamentos_frecuentes',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def get_mascota_datos(self, obj):
        """
        Retorna datos completos de la mascota.
        """
        mascota = obj.mascota

        # Calcular edad si tiene fecha de nacimiento
        edad = None
        if mascota.fecha_nacimiento:
            from datetime import date
            today = date.today()
            edad = today.year - mascota.fecha_nacimiento.year
            if today.month < mascota.fecha_nacimiento.month or \
                    (today.month == mascota.fecha_nacimiento.month and today.day < mascota.fecha_nacimiento.day):
                edad -= 1

        return {
            'id': str(mascota.id),
            'nombre': mascota.nombre,
            'edad': edad,
            'especie': mascota.especie.nombre if mascota.especie else None,
            'raza': mascota.raza.nombre if mascota.raza else "No especificada",
            'sexo': mascota.get_sexo_display(),
            'fecha_nacimiento': mascota.fecha_nacimiento,
            'peso': float(mascota.peso) if mascota.peso else None,
        }

    def get_propietario(self, obj):
        """
        Retorna datos del propietario.
        """
        cliente = obj.mascota.cliente
        usuario = cliente.usuario

        return {
            'usuario_id': str(usuario.id),
            'nombre_completo': usuario.get_full_name(),
            'email': usuario.email,
            'telefono': getattr(cliente, 'telefono', None),
        }

    def get_consultas(self, obj):
        consultas = obj.mascota.consultas.order_by('-fecha_consulta')
        return ConsultaDetailSerializer(
            consultas, many=True, context=self.context
        ).data

    def get_estadisticas(self, obj):
        return obtener_estadisticas_historia(obj)

    def get_medicamentos_frecuentes(self, obj):
        return obtener_medicamentos_frecuentes(obj)


class UltimaConsultaSerializer(serializers.Serializer):
    """
    Serializer para la vista "Ver Ultima Historia Clinica".
    """

    mascota_nombre = serializers.CharField()
    propietario_nombre = serializers.CharField()
    ultima_consulta = ConsultaDetailSerializer()

    def to_representation(self, historia_clinica):
        """
        Transforma la HistoriaClinica en el formato esperado.
        """
        ultima = historia_clinica.mascota.consultas.order_by('-fecha_consulta').first()

        if not ultima:
            return {
                'mascota_nombre': historia_clinica.mascota.nombre,
                'propietario_nombre': historia_clinica.mascota.cliente.usuario.get_full_name(),
                'ultima_consulta': None,
                'mensaje': 'Esta mascota no tiene consultas registradas'
            }

        return {
            'mascota_nombre': historia_clinica.mascota.nombre,
            'propietario_nombre': historia_clinica.mascota.cliente.usuario.get_full_name(),
            'ultima_consulta': ConsultaDetailSerializer(ultima, context=self.context).data
        }