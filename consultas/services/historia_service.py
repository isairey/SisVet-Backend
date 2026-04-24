"""
Servicios de gestión, actualización y construcción de Historias Clínicas.
Aplicación de Composite Pattern + Builder Pattern + Domain Services.
Sara Sanchez
04 Noviembre 2025
"""

from django.db.models import Count
from consultas.models import HistoriaClinica, Prescripcion
from consultas.patterns.composite import HistoriaClinicaCompuesta, ConsultaHoja
from consultas.patterns.builder import HistoriaClinicaBuilder


# -------------------------------------------------------------------
#  SERVICIO PRINCIPAL: CREAR Y ACTUALIZAR HISTORIA CLÍNICA
# -------------------------------------------------------------------

def gestionar_historia_clinica(consulta):
    """
    Crea automáticamente una HistoriaClinica si no existe.
    Actualiza estado de vacunación basado en la consulta.
    Actualiza fecha de actualización.
    """
    historia, _ = HistoriaClinica.objects.get_or_create(
        mascota=consulta.mascota
    )

    vacuna = consulta.vacunas.first()

    if vacuna:
        historia.actualizar_estado_vacunacion(vacuna.estado)

    historia.save()
    return historia


# -------------------------------------------------------------------
#      SERVICIO: GENERAR STRUCTURA COMPOSITE COMPLETA
# -------------------------------------------------------------------

def generar_estructura_historia(historia_clinica):
    """
    Construye toda la estructura Composite de una historia clínica:
    HistoriaClinicaCompuesta -> ConsultaHoja (children)
    """
    raiz = HistoriaClinicaCompuesta(historia_clinica)

    for consulta in historia_clinica.mascota.consultas.all():
        raiz.agregar(ConsultaHoja(consulta))

    return raiz.mostrar()


# -------------------------------------------------------------------
#          SERVICIO: USAR BUILDER PARA ARMAR UNA HISTORIA
# -------------------------------------------------------------------

def crear_historia_completa(
    mascota,
    veterinario,
    descripcion,
    diagnostico,
    medicamento,
    cantidad
):
    """
    Crear historia completa utilizando el Builder Pattern:
    - Crear la historia
    - Agregar consulta
    - Agregar prescripción
    """
    builder = HistoriaClinicaBuilder(mascota)

    historia = (
        builder.crear_historia()
        .agregar_consulta(veterinario, descripcion, diagnostico)
        .agregar_prescripcion(medicamento, cantidad)
        .obtener_historia()
    )

    return historia


# -------------------------------------------------------------------
#        SERVICIOS DE DOMINIO (REGLAS CLÍNICAS Y ESTADÍSTICAS)
# -------------------------------------------------------------------

def obtener_primera_consulta(historia_clinica):
    return (
        historia_clinica.mascota.consultas
        .order_by('fecha_consulta')
        .first()
    )


def obtener_ultima_consulta(historia_clinica):
    return (
        historia_clinica.mascota.consultas
        .order_by('-fecha_consulta')
        .first()
    )


def obtener_estadisticas_historia(historia_clinica):
    """
    - Total consultas
    - Total prescripciones
    - Fechas primera y última consulta
    """
    consultas = historia_clinica.mascota.consultas.all()

    primera = obtener_primera_consulta(historia_clinica)
    ultima = obtener_ultima_consulta(historia_clinica)

    total_prescripciones = sum(
        consulta.prescripciones.count()
        for consulta in consultas
    )

    return {
        'total_consultas': consultas.count(),
        'total_prescripciones': total_prescripciones,
        'primera_consulta': primera.fecha_consulta if primera else None,
        'ultima_consulta': ultima.fecha_consulta if ultima else None,
    }


def obtener_medicamentos_frecuentes(historia_clinica, limite=5):
    """
    Retorna el top de medicamentos más prescritos en la historia.
    """
    mascota = historia_clinica.mascota

    medicamentos = (
        Prescripcion.objects.filter(consulta__mascota=mascota)
        .values('medicamento__descripcion')
        .annotate(veces_prescrito=Count('id'))
        .order_by('-veces_prescrito')[:limite]
    )

    return [
        {
            'medicamento': med['medicamento__descripcion'],
            'veces_prescrito': med['veces_prescrito']
        }
        for med in medicamentos
    ]
