"""
Configuración del panel de administración para el módulo de Consultas.

Registra los modelos con interfaces personalizadas para gestión desde /admin/
Sara Sanchez
02 Noviembre 2025
"""

from django.contrib import admin
from django.urls import reverse
from .models import (
    Consulta,
    HistoriaClinica,
    Prescripcion,
    Examen,
    HistorialVacuna
)

ADMIN_CONSULTA_CHANGE = 'admin:consultas_consulta_change'
ADMIN_MASCOTA_CHANGE = 'admin:mascotas_mascota_change'
ADMIN_USER_CHANGE = 'admin:auth_user_change'
ADMIN_PRODUCTO_CHANGE = 'admin:inventario_producto_change'
ADMIN_CONSULTA_CHANGELIST = 'admin:consultas_consulta_changelist'

#Modelos relacionados dentro de otros

class PrescripcionInline(admin.TabularInline):
    """
    Permite agregar/editar medicamentos directamente desde la consulta.
    """
    model = Prescripcion
    extra = 1  # Número de formularios vacíos a mostrar
    min_num = 0  # Mínimo de prescripciones (puede no tener ninguna)
    fields = ['medicamento', 'cantidad', 'indicaciones']
    autocomplete_fields = ['medicamento']
    verbose_name = "Prescripción"
    verbose_name_plural = "Prescripciones (Medicamentos)"


class ExamenInline(admin.TabularInline):
    """
    mostrar exámenes dentro de una consulta.
    """
    model = Examen
    extra = 1
    min_num = 0
    fields = ['tipo_examen', 'descripcion']
    verbose_name = "Examen"
    verbose_name_plural = "Exámenes a Realizar"

class HistorialVacunaInline(admin.StackedInline):
    """
     mostrar registro de vacunas dentro de una consulta.
    """
    model = HistorialVacuna
    extra = 0
    max_num = 1
    fields = ['estado', 'vacunas_descripcion']
    verbose_name = "Estado de Vacunación"
    verbose_name_plural = "Estado de Vacunación"

# ADMIN: CONSULTA (Principal)

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    """
    Incluye información de la mascota, veterinario, prescripciones y exámenes.
    """
    list_display = [
        'id',
        'mascota_link',
        'veterinario_link',
        'fecha_consulta',
        'diagnostico_corto',
        'total_prescripciones_display',
        'total_examenes_display',
        'estado_vacunacion_display',
        'created_at'
    ]

    list_filter = [
        'fecha_consulta',
        'veterinario',
        'created_at',
    ]

    search_fields = [
        'mascota__nombre',
        'mascota__propietario__first_name',
        'mascota__propietario__last_name',
        'diagnostico',
        'descripcion_consulta',
    ]

    date_hierarchy = 'fecha_consulta'
    ordering = ['-fecha_consulta']

    readonly_fields = [
        'created_at',
        'updated_at',
        'datos_personales_display',
        'total_prescripciones_display',
        'total_examenes_display',
    ]

    autocomplete_fields = ['veterinario', 'mascota']

    fieldsets = (
        ('Información General', {
            'fields': (
                'mascota',
                'veterinario',
                'fecha_consulta',
            )
        }),
        ('Datos de la Consulta', {
            'fields': (
                'datos_personales_display',
                'descripcion_consulta',
                'diagnostico',
                'notas_adicionales',
            )
        }),
        ('Auditoría', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    inlines = [
        HistorialVacunaInline,
        PrescripcionInline,
        ExamenInline,
    ]

    list_per_page = 25

    @admin.display(description='Mascota', ordering='mascota__nombre')
    def mascota_link(self, obj):
        """Muestra el nombre de la mascota como enlace al detalle"""
        return obj.mascota.nombre

    @admin.display(description='Veterinario', ordering='veterinario__first_name')
    def veterinario_link(self, obj):
        """Muestra el nombre completo del veterinario"""
        if obj.veterinario and hasattr(obj.veterinario, 'user'):
            return obj.veterinario.user.get_full_name() or obj.veterinario.user.username
        return '-'

    @admin.display(description='Diagnóstico')
    def diagnostico_corto(self, obj):
        """Muestra versión resumida del diagnóstico (máximo 50 caracteres)"""
        if len(obj.diagnostico) > 50:
            return f"{obj.diagnostico[:50]}..."
        return obj.diagnostico

    @admin.display(description='Datos Personales')
    def datos_personales_display(self, obj):
        """
        Muestra información consolidada de la mascota en formato texto.
        """
        datos = obj.get_datos_personales()
        return (
            f"Mascota: {datos['nombre_mascota']}\n"
            f"Propietario: {datos['nombre_propietario']}\n"
            f"Edad: {datos['edad']}\n"
            f"Especie: {datos['tipo_especie']}\n"
            f"Raza: {datos['raza']}\n"
            f"Estado Vacunación: {datos['estado_vacunacion']}"
        )

    @admin.display(description='Prescripciones')
    def total_prescripciones_display(self, obj):
        """Muestra el total de medicamentos prescritos"""
        total = obj.get_prescripciones_count()
        return f"{total} medicamento(s)" if total > 0 else "Sin prescripciones"

    @admin.display(description='Exámenes')
    def total_examenes_display(self, obj):
        """Muestra el total de exámenes ordenados"""
        total = obj.get_examenes_count()
        return f"{total} examen(es)" if total > 0 else "Sin exámenes"

    @admin.display(description='Vacunación')
    def estado_vacunacion_display(self, obj):
        """Muestra el estado actual de vacunación de la mascota"""
        estado = obj.get_estado_vacunacion_consulta()
        return estado or "No registrado"

# ADMIN: HISTORIA CLÍNICA

@admin.register(HistoriaClinica)
class HistoriaClinicaAdmin(admin.ModelAdmin):
    """
    Administración de Historias Clínicas consolidadas.
    """
    list_display = [
        'id',
        'mascota_link',
        'propietario_display',
        'total_consultas_display',
        'estado_vacunacion_badge',
        'fecha_actualizacion'
    ]

    list_filter = [
        'estado_vacunacion_actual',
        'fecha_creacion',
        'fecha_actualizacion',
    ]

    search_fields = [
        'mascota__nombre',
        'mascota__cliente__usuario__nombre',
        'mascota__cliente__usuario__apellido',
    ]

    date_hierarchy = 'fecha_actualizacion'
    ordering = ['-fecha_actualizacion']

    readonly_fields = [
        'mascota',
        'fecha_creacion',
        'fecha_actualizacion',
        'estado_vacunacion_actual',
        'total_consultas_display',
        'ultima_consulta_display',
        'medicamentos_frecuentes_display',
    ]

    fieldsets = (
        ('Mascota', {
            'fields': (
                'mascota',
                'total_consultas_display',
            )
        }),
        ('Vacunación', {
            'fields': (
                'estado_vacunacion_actual',
            )
        }),
        ('Fechas', {
            'fields': (
                'fecha_creacion',
                'fecha_actualizacion',
            ),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        """Deshabilita creación manual (se crea automáticamente con señales)"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Deshabilita eliminación manual (se elimina con la mascota)"""
        return False

    @admin.display(description='Mascota', ordering='mascota__nombre')
    def mascota_link(self, obj):
        """Muestra el nombre de la mascota"""
        return obj.mascota.nombre

    @admin.display(description='Propietario')
    def propietario_display(self, obj):
        """Muestra el nombre completo del propietario"""
        if hasattr(obj.mascota.cliente, 'get_full_name'):
            return obj.mascota.cliente.get_full_name()
        return str(obj.mascota.cliente)

    @admin.display(description='Total Consultas')
    def total_consultas_display(self, obj):
        """Muestra el número total de consultas de la mascota"""
        total = obj.get_total_consultas()
        return f"{total} consulta(s)"

    @admin.display(description='Estado Vacunación')
    def estado_vacunacion_badge(self, obj):
        """Muestra el estado actual de vacunación"""
        return obj.get_estado_vacunacion_actual_display()

    @admin.display(description='Última Consulta')
    def ultima_consulta_display(self, obj):
        """
        Muestra información resumida de la última consulta.
        """
        ultima = obj.get_ultima_consulta()
        if ultima:
            return (
                f"Fecha: {ultima.fecha_consulta.strftime('%d/%m/%Y')}\n"
                f"Diagnóstico: {ultima.diagnostico[:50]}"
            )
        return 'Sin consultas'

    @admin.display(description='Medicamentos Frecuentes')
    def medicamentos_frecuentes_display(self, obj):
        """
        Lista los 3 medicamentos más prescritos con su frecuencia.
        """
        medicamentos = obj.get_medicamentos_frecuentes(limit=3)
        if medicamentos:
            lista_meds = [
                f"{med['medicamento__nombre']} ({med['cantidad_prescripciones']}x)"
                for med in medicamentos
            ]
            return ", ".join(lista_meds)
        return 'Sin prescripciones'

# ADMIN: PRESCRIPCIÓN

@admin.register(Prescripcion)
class PrescripcionAdmin(admin.ModelAdmin):
    """
    Muestra información de stock y permite vincular con consultas.
    """

    list_display = [
        'id',
        'consulta_link',
        'mascota_display',
        'medicamento_link',
        'cantidad',
        'stock_disponible_display',
        'fecha_prescripcion'
    ]

    list_filter = [
        'fecha_prescripcion',
        'medicamento',
    ]

    search_fields = [
        'consulta__mascota__nombre',
        'medicamento__descripcion',
        'indicaciones',
    ]

    date_hierarchy = 'fecha_prescripcion'
    ordering = ['-fecha_prescripcion']

    readonly_fields = ['fecha_prescripcion', 'stock_disponible_display']
    autocomplete_fields = ['consulta', 'medicamento']

    fieldsets = (
        ('Consulta', {
            'fields': ('consulta',)
        }),
        ('Medicamento', {
            'fields': (
                'medicamento',
                'cantidad',
                'stock_disponible_display',
                'indicaciones',
            )
        }),
        ('Fecha', {
            'fields': ('fecha_prescripcion',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Consulta')
    def consulta_link(self, obj):
        """Muestra el ID de la consulta"""
        return f"Consulta #{obj.consulta.id}"

    @admin.display(description='Mascota')
    def mascota_display(self, obj):
        """Muestra el nombre de la mascota asociada"""
        return obj.consulta.mascota.nombre

    @admin.display(description='Medicamento')
    def medicamento_link(self, obj):
        """Muestra la descripción del medicamento"""
        return obj.medicamento.descripcion

    @admin.display(description='Stock Disponible')
    def stock_disponible_display(self, obj):
        """
        Muestra el stock actual del medicamento.
        """
        stock = obj.medicamento.stock
        stock_minimo = obj.medicamento.stock_minimo

        if stock <= stock_minimo:
            nivel = "CRÍTICO"
        elif stock <= stock_minimo * 2:
            nivel = "BAJO"
        else:
            nivel = "NORMAL"

        return f"{stock} unidades ({nivel})"

# ADMIN: EXAMEN

@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    """
    Administración de Exámenes médicos ordenados durante consultas.
    """
    list_display = [
        'id',
        'consulta_link',
        'mascota_display',
        'tipo_examen_badge',
        'descripcion_corta',
        'fecha_orden'
    ]

    list_filter = [
        'tipo_examen',
        'fecha_orden',
    ]

    search_fields = [
        'consulta__mascota__nombre',
        'descripcion',
        'tipo_examen',
    ]

    date_hierarchy = 'fecha_orden'
    ordering = ['-fecha_orden']

    readonly_fields = ['fecha_orden']
    autocomplete_fields = ['consulta']

    fieldsets = (
        ('Consulta', {
            'fields': ('consulta',)
        }),
        ('Examen', {
            'fields': (
                'tipo_examen',
                'descripcion',
            )
        }),
        ('Fecha', {
            'fields': ('fecha_orden',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Consulta')
    def consulta_link(self, obj):
        """Muestra el ID de la consulta"""
        return f"Consulta #{obj.consulta.id}"

    @admin.display(description='Mascota')
    def mascota_display(self, obj):
        """Muestra el nombre de la mascota"""
        return obj.consulta.mascota.nombre

    @admin.display(description='Tipo de Examen')
    def tipo_examen_badge(self, obj):
        """Muestra el tipo de examen legible"""
        return obj.get_tipo_examen_display()

    @admin.display(description='Descripción')
    def descripcion_corta(self, obj):
        """Muestra versión resumida de la descripción (máximo 50 caracteres)"""
        if obj.descripcion:
            if len(obj.descripcion) > 50:
                return f"{obj.descripcion[:50]}..."
            return obj.descripcion
        return '-'

# ADMIN: HISTORIAL DE VACUNAS

@admin.register(HistorialVacuna)
class HistorialVacunaAdmin(admin.ModelAdmin):
    """
    Administración de Historial de Vacunas registrado por consulta.
    """
    list_display = [
        'id',
        'consulta_link',
        'mascota_display',
        'estado_badge',
        'vacunas_descripcion_corta',
        'fecha_registro'
    ]

    list_filter = [
        'estado',
        'fecha_registro',
    ]

    search_fields = [
        'consulta__mascota__nombre',
        'vacunas_descripcion',
    ]

    date_hierarchy = 'fecha_registro'
    ordering = ['-fecha_registro']

    readonly_fields = ['fecha_registro']
    autocomplete_fields = ['consulta']

    fieldsets = (
        ('Consulta', {
            'fields': ('consulta',)
        }),
        ('Vacunación', {
            'fields': (
                'estado',
                'vacunas_descripcion',
            )
        }),
        ('Fecha', {
            'fields': ('fecha_registro',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Consulta')
    def consulta_link(self, obj):
        """Muestra el ID de la consulta"""
        return f"Consulta #{obj.consulta.id}"

    @admin.display(description='Mascota')
    def mascota_display(self, obj):
        """Muestra el nombre de la mascota"""
        return obj.consulta.mascota.nombre

    @admin.display(description='Estado')
    def estado_badge(self, obj):
        """Muestra el estado de vacunación legible"""
        return obj.get_estado_display()

    @admin.display(description='Vacunas')
    def vacunas_descripcion_corta(self, obj):
        """Muestra versión resumida de las vacunas (máximo 40 caracteres)"""
        if obj.vacunas_descripcion:
            if len(obj.vacunas_descripcion) > 40:
                return f"{obj.vacunas_descripcion[:40]}..."
            return obj.vacunas_descripcion
        return '-'