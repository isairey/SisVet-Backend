from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from inventario.models import Kardex


@receiver(post_save, sender=Kardex)
def procesar_kardex_al_guardar(sender, instance, created, **kwargs):
    """
    Signal POST_SAVE: Se dispara DESPUÉS de guardar un Kardex.

    Si es un NUEVO registro (created=True):
    - Procesa el movimiento mediante KardexService.
    - Usa un flag transitorio en la instancia para evitar re-entradas.
    """
    if not created:
        return

    # Evitar re-entradas
    if getattr(instance, '_ya_procesado', False):
        return

    from inventario.services.kardex_service import KardexService

    # Marcar antes de procesar para evitar re-entradas si algo hace saves recursivos.
    instance._ya_procesado = True

    servicio = KardexService()
    servicio.procesar_movimiento(instance)


@receiver(pre_delete, sender=Kardex)
def anular_kardex_al_eliminar(sender, instance, **kwargs):
    """
    Signal PRE_DELETE: Se dispara ANTES de eliminar un Kardex.

    Llama a anular_movimiento() que revierte todo.
    """
    # No hacer nada si ya está anulado
    if instance.detalle and "ANULADO" in instance.detalle:
        return

    from inventario.services.kardex_service import KardexService

    servicio = KardexService()
    servicio.anular_movimiento(instance)