"""
Servicios de lógica de negocio relacionados con las Consultas
Sara Sanchez
03 Noviembre 2025
"""

from django.db import transaction
from citas.patterns.state.state_factory import EstadoCitaFactory
from consultas.models import (
    Consulta,
    Prescripcion,
    Examen
)
from consultas.models import HistorialVacuna
from decimal import Decimal
from rest_framework.exceptions import ValidationError



@transaction.atomic
def crear_consulta_completa(validated_data):
    """
    Crea una Consulta completa con prescripciones, exámenes y vacunas,
    garantizando integridad con transacciones.
    """

    # Extraer datos anidados
    prescripciones_data = validated_data.pop('prescripciones', [])
    examenes_data = validated_data.pop('examenes', [])
    vacunas_data = validated_data.pop('vacunas', None)

    # Crear consulta principal
    consulta = Consulta.objects.create(**validated_data)

    if consulta.cita:
        try:
            # Obtenemos el manejador del estado actual de la cita (Ej: EstadoAgendada)
            estado_handler = EstadoCitaFactory.obtener_estado(consulta.cita.estado)

            # Ejecutamos la transición a 'COMPLETADA'
            estado_handler.completar(consulta.cita)

        except Exception as e:
            # Opcional: Loguear el error, pero no interrumpir la creación de la consulta
            # o lanzar un error si es estricto que la cita cambie de estado.
            print(f"Advertencia: No se pudo completar la cita {consulta.cita.id}: {e}")

    # Crear prescripciones
    for p_data in prescripciones_data:
        Prescripcion.objects.create(
            consulta=consulta,
            **p_data
        )

    # Crear exámenes
    for e_data in examenes_data:
        Examen.objects.create(
            consulta=consulta,
            **e_data
        )

    # Crear registro de vacunas
    if vacunas_data:
        # Asegurar que vacunas_descripcion nunca sea None
        if vacunas_data.get('vacunas_descripcion') is None:
            vacunas_data['vacunas_descripcion'] = ""
        HistorialVacuna.objects.create(
            consulta=consulta,
            **vacunas_data
        )

    return consulta

def crear_consulta(data, veterinario):
    """
    Crea una consulta y procesa su historia clínica, vacunas, etc.
    """
    consulta = Consulta.objects.create(
        veterinario=veterinario,
        **data
    )

    # ▶ Aquí llamas a servicios externos:
    from .historia_service import gestionar_historia_clinica
    gestionar_historia_clinica(consulta)

    return consulta


@transaction.atomic
def actualizar_consulta_completa(instance, validated_data):
    """
    Actualiza una consulta completa.
    IMPORTANTE: Desactivamos temporalmente los signals para manejar el inventario manualmente.
    """
    from consultas.models import Prescripcion, Examen, HistorialVacuna as Vacuna
    from django.db.models.signals import post_save, pre_delete
    from consultas.signals import actualizar_inventario_post_save, restaurar_stock_al_eliminar_prescripcion


    # Actualizar datos básicos
    instance.mascota = validated_data.get('mascota', instance.mascota)
    instance.fecha_consulta = validated_data.get('fecha_consulta', instance.fecha_consulta)
    instance.descripcion_consulta = validated_data.get('descripcion_consulta', instance.descripcion_consulta)
    instance.diagnostico = validated_data.get('diagnostico', instance.diagnostico)
    instance.notas_adicionales = validated_data.get('notas_adicionales', instance.notas_adicionales)
    instance.servicio = validated_data.get('servicio', instance.servicio)
    instance.cita = validated_data.get('cita', instance.cita)
    instance.save()

    # DESCONECTAR SIGNALS TEMPORALMENTE
    post_save.disconnect(actualizar_inventario_post_save, sender=Prescripcion)
    pre_delete.disconnect(restaurar_stock_al_eliminar_prescripcion, sender=Prescripcion)

    try:
        # Actualizar prescripciones
        if 'prescripciones' in validated_data:
            prescripciones_data = validated_data.pop('prescripciones')

            for old_prescripcion in instance.prescripciones.all():
                producto = old_prescripcion.medicamento
                cantidad = Decimal(old_prescripcion.cantidad)
                producto.stock += cantidad
                producto.save(update_fields=["stock"])
                print(f"   ✓ Stock restaurado: {producto.nombre} +{cantidad}")

            instance.prescripciones.all().delete()

            for prescripcion_data in prescripciones_data:
                medicamento = prescripcion_data['medicamento']
                cantidad = Decimal(prescripcion_data['cantidad'])
                indicaciones = prescripcion_data['indicaciones']

                # Validar y descontar stock
                if medicamento.stock < cantidad:
                    raise ValidationError({
                        'prescripciones': f'Stock insuficiente para {medicamento.nombre}. Disponible: {medicamento.stock}, solicitado: {cantidad}'
                    })

                medicamento.stock -= cantidad
                medicamento.save(update_fields=["stock"])
                print(f"   ✓ Stock descontado: {medicamento.nombre} -{cantidad}")

                # Crear prescripción
                Prescripcion.objects.create(
                    consulta=instance,
                    medicamento=medicamento,
                    cantidad=cantidad,
                    indicaciones=indicaciones
                )
                print(f"   ✓ Prescripción creada")

        # Actualizar exámenes
        if 'examenes' in validated_data:
            instance.examenes.all().delete()
            examenes_data = validated_data.pop('examenes')
            for examen_data in examenes_data:
                Examen.objects.create(consulta=instance, **examen_data)

        # Actualizar vacunas
        if 'vacunas' in validated_data:
            instance.vacunas.all().delete()
            vacunas_data = validated_data.pop('vacunas')
            Vacuna.objects.create(consulta=instance, **vacunas_data)
        return instance

    finally:
        # RECONECTAR SIGNALS
        post_save.connect(actualizar_inventario_post_save, sender=Prescripcion)
        pre_delete.connect(restaurar_stock_al_eliminar_prescripcion, sender=Prescripcion)


def obtener_datos_personales(consulta):
    """Obtiene los datos personales del cliente de la mascota"""
    mascota = consulta.mascota
    cliente = getattr(mascota, "cliente", None)

    if not cliente:
        return None

    return {
        "nombre": f"{cliente.usuario.nombre} {cliente.usuario.apellido}",
        "telefono": getattr(cliente, "telefono", None),
        "direccion": getattr(cliente, "direccion", None),
    }