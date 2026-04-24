from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from transacciones.models.detalle_factura import DetalleFactura
from transacciones.models.factura import Factura
from django.db.models.signals import post_save
from django.dispatch import receiver
from transacciones.models.pago import Pago
from transacciones.patterns.state_factory import EstadoFacturaFactory

@receiver(post_save, sender=DetalleFactura)
def detalle_guardado_recalcular(sender, instance, created, **kwargs):
    """
    Cuando un detalle se guarda, recalcular la factura asociada.
    """
    factura = instance.factura
    if factura:
        factura.recalcular_totales()

@receiver(post_delete, sender=DetalleFactura)
def detalle_eliminado_recalcular(sender, instance, **kwargs):
    factura = instance.factura
    if factura:
        factura.recalcular_totales()


@receiver(post_save, sender=Pago)
def actualizar_factura_cuando_se_crea_pago(sender, instance, created, **kwargs):
    """
    Cuando se crea un Pago (vía admin o API), se actualiza el estado de la factura
    usando el patrón State existente.
    """

    if not created:
        return

    factura = instance.factura

    # Obtener el estado actual de la factura
    estado = EstadoFacturaFactory.obtener_estado(factura.estado)

    # Aplicar método pagar() del patrón State
    estado.pagar(factura)

    # Descontar inventario usando la lógica actual del servicio
    for detalle in factura.detalles.all():
        if detalle.producto:
            detalle.producto.stock -= detalle.cantidad
            detalle.producto.save()

    factura.save()