"""
Señales automáticas del módulo de Consultas y Prescripciones
Sara Sanchez
03 Noviembre 2025
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver, Signal
from .models import Consulta, Prescripcion, HistoriaClinica
from .services.historia_service import gestionar_historia_clinica
from .services.prescripcion_service import descontar_inventario, devolver_inventario
from .patterns.memento import GestorMementos

gestor_mementos = GestorMementos()

# --- SEÑALES PERSONALIZADAS (BENGALAS) ---

# Señal para cuando se finaliza la consulta (ej. para enviar resumen)
consulta_finalizada_signal = Signal()

# Señal para cuando se envía la solicitud de consentimiento
consulta_consentimiento_signal = Signal()


@receiver(post_save, sender=Consulta)
def crear_o_actualizar_historia(sender, instance, created, **kwargs):
    """
    Al crear una consulta, crea/actualiza la historia clínica
    Y AHORA, notifica al cliente si es creada.
    """
    if created:
        print(f"Nueva consulta creada: {instance.id}")
        gestionar_historia_clinica(instance)

        # Disparamos la señal de "consulta finalizada"
        try:
            consulta_finalizada_signal.send(sender=Consulta, consulta=instance)
            print(f"Señal 'consulta_finalizada' enviada para consulta {instance.id}")
        except Exception as e:
            print(f"Error al enviar señal de consulta: {e}")

@receiver(post_save, sender=Prescripcion)
def actualizar_inventario_post_save(sender, instance, created, **kwargs):
    """
    Descuenta del inventario cuando se crea una prescripción.
    Evita duplicar la operación si se guarda dos veces.
    """
    # Solo ejecutar si es una nueva prescripción
    if not created:
        return

    # Evitar duplicados si ya se procesó
    if hasattr(instance, "_stock_actualizado"):
        return

    try:
        descontar_inventario(
            producto=instance.medicamento,
            cantidad=instance.cantidad,
            detalle=f"Salida por prescripción (Consulta #{instance.consulta.id})"
        )
        # Marcar como procesado para evitar duplicados
        instance._stock_actualizado = True
        print(f"✓ Stock descontado correctamente para {instance.medicamento.descripcion}")
    except Exception as e:
        print(f"✗ Error al descontar stock: {e}")
        raise  # Re-lanzar para que no se guarde la prescripción si falla


@receiver(pre_delete, sender=Prescripcion)
def restaurar_stock_al_eliminar_prescripcion(sender, instance, **kwargs):
    """
    Cuando se elimina una prescripción, se devuelve el stock al inventario.
    """
    try:
        devolver_inventario(
            instance,
            detalle=f"Devolución automática por eliminación de prescripción (Consulta #{instance.consulta.id})"
        )
        print(f"✓ Stock restaurado para {instance.medicamento.descripcion}")
    except Exception as e:
        print(f"✗ Error al restaurar stock: {e}")
        raise


@receiver(post_save, sender=HistoriaClinica)
def guardar_version_historia(sender, instance, **kwargs):
    """
    Guarda una versión de la historia clínica usando el patrón Memento.
    """
    gestor_mementos.guardar(instance)