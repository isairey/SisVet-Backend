from decimal import Decimal
from django.db.models.signals import post_save
from inventario.models import Kardex

"""
Servicios de dominio para gestión de prescripciones y actualización de inventario.
"""

def descontar_inventario(producto, cantidad, detalle="Salida por prescripción"):
    cantidad = Decimal(cantidad)

    if producto.stock < cantidad:
        raise ValueError(
            f"Stock insuficiente para {producto.descripcion}. "
            f"Disponible: {producto.stock}, solicitado: {cantidad}"
        )

    producto.stock -= cantidad
    producto.save(update_fields=["stock"])

    from inventario.signals.kardex_signals import procesar_kardex_al_guardar
    post_save.disconnect(procesar_kardex_al_guardar, sender=Kardex)

    try:
        Kardex.objects.create(
            tipo="salida",
            cantidad=cantidad,
            detalle=detalle,
            producto=producto,
        )
    finally:
        post_save.connect(procesar_kardex_al_guardar, sender=Kardex)

    return producto


def devolver_inventario(prescripcion, detalle="Devolución por eliminación de prescripción"):
    producto = prescripcion.medicamento
    cantidad = Decimal(prescripcion.cantidad)

    producto.stock += cantidad
    producto.save(update_fields=["stock"])

    from inventario.signals.kardex_signals import procesar_kardex_al_guardar
    post_save.disconnect(procesar_kardex_al_guardar, sender=Kardex)

    try:
        Kardex.objects.create(
            tipo="entrada",
            cantidad=cantidad,
            detalle=detalle,
            producto=producto,
        )
    finally:
        post_save.connect(procesar_kardex_al_guardar, sender=Kardex)

    return producto
