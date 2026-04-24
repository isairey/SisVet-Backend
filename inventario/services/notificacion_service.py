from datetime import timedelta
from django.utils import timezone
from inventario.models import Notificacion, Producto


class NotificacionService:

    def crear_info(self, titulo: str, mensaje: str):
        """Crea una notificación de información sin duplicados."""
        Notificacion.objects.get_or_create(
            titulo=titulo,
            mensaje=mensaje,
            modulo="inventario",
            nivel="info"
        )

    def crear_warning(self, titulo: str, mensaje: str):
        Notificacion.objects.get_or_create(
            titulo=titulo,
            mensaje=mensaje,
            modulo="inventario",
            nivel="warning"
        )

    def crear_error(self, titulo: str, mensaje: str):
        Notificacion.objects.get_or_create(
            titulo=titulo,
            mensaje=mensaje,
            modulo="inventario",
            nivel="error"
        )

    def verificar_alertas_producto(self, producto: Producto):
        """Verifica stock mínimo + vencimiento."""
        self._verificar_stock_minimo(producto)
        self._verificar_vencimiento(producto)

    def _verificar_stock_minimo(self, producto: Producto):
        if producto.stock <= producto.stock_minimo:
            self.crear_warning(
                f"Stock mínimo alcanzado: {producto.nombre}",
                f"El producto '{producto.nombre}' tiene {producto.stock} unidades (mínimo {producto.stock_minimo})."
            )
        else:
            Notificacion.objects.filter(
                titulo__icontains="Stock mínimo",
                mensaje__icontains=producto.nombre
            ).delete()

    def _verificar_vencimiento(self, producto: Producto):
        if not producto.fecha_vencimiento:
            Notificacion.objects.filter(
                mensaje__icontains=producto.nombre,
                titulo__icontains="Producto"
            ).delete()
            return

        hoy = timezone.now().date()
        limite = hoy + timedelta(days=30)

        if producto.fecha_vencimiento < hoy:
            self.crear_error(
                f"Producto vencido: {producto.nombre}",
                f"El producto '{producto.nombre}' venció el {producto.fecha_vencimiento}."
            )

        elif hoy <= producto.fecha_vencimiento <= limite:
            self.crear_warning(
                f"Producto por vencer: {producto.nombre}",
                f"El producto '{producto.nombre}' vence el {producto.fecha_vencimiento}."
            )

        else:
            Notificacion.objects.filter(
                titulo__icontains="Producto por vencer",
                mensaje__icontains=producto.nombre
            ).delete()

    def marcar_como_leida(self, notificacion_id: int):
        n = Notificacion.objects.filter(id=notificacion_id).first()
        if not n:
            raise ValueError(f"No existe la notificación con ID {notificacion_id}")
        n.leida = True
        n.save(update_fields=['leida'])

    def marcar_todas_como_leidas(self, modulo=None) -> int:
        qs = Notificacion.objects.filter(leida=False)
        if modulo:
            qs = qs.filter(modulo=modulo)
        return qs.update(leida=True)

    def eliminar_notificaciones_producto(self, producto: Producto) -> int:
        count, _ = Notificacion.objects.filter(
            mensaje__icontains=producto.nombre
        ).delete()
        return count
