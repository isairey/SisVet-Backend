from datetime import datetime
from django.db import transaction
from django.conf import settings
from transacciones.models.factura import Factura
from transacciones.models.pago import Pago
from transacciones.models.detalle_factura import DetalleFactura
from citas.models import Cita
from consultas.models import Consulta
from django.core.exceptions import ValidationError
from transacciones.patterns.state_factory import EstadoFacturaFactory
from notificaciones.patterns.strategies.factura_email import (
    FacturaGeneradaEmail, 
    FacturaPagadaEmail, 
    FacturaEnvioManualEmail,
    FacturaVentaDirectaEmail
)


class FacturaService:

    @staticmethod
    def crear_factura_desde_cita(cita_id):
        """
        Crea una factura desde una cita.
        Previene duplicados: si ya existe una factura para esta cita, lanza ValidationError.
        """
        try:
            cita = Cita.objects.get(id=cita_id)
        except Cita.DoesNotExist:
            raise ValidationError("La cita no existe.")

        if not cita.servicio:
            raise ValidationError("La cita no tiene un servicio asignado.")

        # Verificar si ya existe una factura para esta cita
        factura_existente = Factura.objects.filter(cita=cita).exclude(estado='ANULADA').first()
        if factura_existente:
            raise ValidationError(
                f"Ya existe una factura (ID: {factura_existente.id}) para esta cita. "
                "Solo se puede reenviar el correo de la factura existente."
            )

        factura = Factura.objects.create(
            cliente=cita.mascota.cliente.usuario,
            cita=cita,
            total=0
        )

        # Crear detalle por el servicio
        DetalleFactura.objects.create(
            factura=factura,
            servicio=cita.servicio,
            cantidad=1,
            precio_unitario=cita.servicio.costo, 
            subtotal=cita.servicio.costo
        )

        factura.recalcular_totales()

        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        context = {
            "cliente_nombre": factura.cliente.get_full_name(),
            "factura_id": factura.id,
            "fecha_emision": factura.fecha.strftime("%d/%m/%Y %H:%M"),
            "estado": factura.estado,
            "total": factura.total,
            "detalles": factura.detalles.all(),
            "url_historial": f"{frontend_url}/app/facturacion/{factura.id}",
            "anio_actual": datetime.now().year,
        }

        FacturaGeneradaEmail(context, factura.cliente.email).send()

        return factura

    @staticmethod
    def crear_factura_desde_consulta(consulta_id):
        """
        Crea una factura desde una consulta.
        Previene duplicados: si ya existe una factura para esta consulta, lanza ValidationError.
        """
        try:
            consulta = Consulta.objects.get(id=consulta_id)
        except Consulta.DoesNotExist:
            raise ValidationError("La consulta no existe.")

        # Verificar si ya existe una factura para esta consulta
        factura_existente = Factura.objects.filter(consulta=consulta).exclude(estado='ANULADA').first()
        if factura_existente:
            raise ValidationError(
                f"Ya existe una factura (ID: {factura_existente.id}) para esta consulta. "
                "Solo se puede reenviar el correo de la factura existente."
            )

        factura = Factura.objects.create(
            cliente=consulta.mascota.cliente.usuario,
            consulta=consulta,
            total=0
        )

        # Agregar productos prescritos (medicamentos)
        for prescripcion in consulta.prescripciones.all():
            producto = prescripcion.medicamento   

            DetalleFactura.objects.create(
                factura=factura,
                producto=producto,                
                cantidad=prescripcion.cantidad,
                precio_unitario=producto.precio_venta, 
                subtotal=producto.precio_venta * prescripcion.cantidad
            )

        factura.recalcular_totales()

        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        context = {
            "cliente_nombre": factura.cliente.get_full_name(),
            "factura_id": factura.id,
            "fecha_emision": factura.fecha.strftime("%d/%m/%Y %H:%M"),
            "estado": factura.estado,
            "total": factura.total,
            "detalles": factura.detalles.all(),
            "url_historial": f"{frontend_url}/app/facturacion/{factura.id}",
            "anio_actual": datetime.now().year,
        }

        FacturaGeneradaEmail(context, factura.cliente.email).send()
        
        return factura

    @staticmethod
    def reenviar_factura_email(factura_id):
        """
        Reenvía el correo de una factura existente.
        """
        try:
            factura = Factura.objects.get(id=factura_id)
        except Factura.DoesNotExist:
            raise ValidationError("La factura no existe.")

        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        context = {
            "cliente_nombre": factura.cliente.get_full_name(),
            "factura_id": factura.id,
            "fecha_emision": factura.fecha.strftime("%d/%m/%Y %H:%M"),
            "estado": factura.estado,
            "total": factura.total,
            "detalles": factura.detalles.all(),
            "url_historial": f"{frontend_url}/app/facturacion/{factura.id}",
            "anio_actual": datetime.now().year,
        }

        FacturaEnvioManualEmail(context, factura.cliente.email).send()

        return factura

    @staticmethod
    @transaction.atomic
    def crear_factura_desde_productos(cliente_id, productos_data, usuario=None):
        """
        Crea una factura desde productos (venta directa desde inventario).
        
        Args:
            cliente_id: ID del cliente que realiza la compra
            productos_data: Lista de diccionarios con formato:
                [{"producto_id": 1, "cantidad": 2}, {"producto_id": 3, "cantidad": 1}]
            usuario: Usuario que realiza la operación (para Kardex)
        
        Returns:
            Factura creada
        
        Raises:
            ValidationError: Si hay problemas de validación, stock insuficiente o duplicados
        """
        from inventario.models import Producto, Kardex
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            cliente = User.objects.get(id=cliente_id)
        except User.DoesNotExist:
            raise ValidationError("El cliente no existe.")

        if not productos_data or not isinstance(productos_data, list):
            raise ValidationError("Debe proporcionar una lista de productos.")

        # Validar que no haya productos duplicados en la misma solicitud
        producto_ids = [item.get("producto_id") for item in productos_data]
        if len(producto_ids) != len(set(producto_ids)):
            raise ValidationError("No se pueden incluir productos duplicados en la misma factura.")

        # Validar productos y stock antes de crear la factura
        productos_validados = []
        for item in productos_data:
            producto_id = item.get("producto_id")
            cantidad = item.get("cantidad", 1)

            if not producto_id:
                raise ValidationError("Cada producto debe tener un 'producto_id' válido.")

            if cantidad <= 0:
                raise ValidationError(f"La cantidad debe ser mayor a 0 para el producto {producto_id}.")

            try:
                producto = Producto.objects.get(id=producto_id, activo=True)
            except Producto.DoesNotExist:
                raise ValidationError(f"El producto con ID {producto_id} no existe o está inactivo.")

            # Validar stock disponible
            if producto.stock < cantidad:
                raise ValidationError(
                    f"Stock insuficiente para '{producto.nombre}'. "
                    f"Stock disponible: {producto.stock}, solicitado: {cantidad}."
                )

            productos_validados.append({
                "producto": producto,
                "cantidad": cantidad
            })

        # Crear la factura
        factura = Factura.objects.create(
            cliente=cliente,
            total=0
        )

        # Crear detalles y registrar movimientos en Kardex
        for item in productos_validados:
            producto = item["producto"]
            cantidad = item["cantidad"]

            # Crear detalle de factura
            DetalleFactura.objects.create(
                factura=factura,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio_venta,
                subtotal=producto.precio_venta * cantidad
            )

            # Registrar movimiento en Kardex (salida)
            Kardex.objects.create(
                tipo='salida',
                producto=producto,
                cantidad=cantidad,
                detalle=f"Venta directa - Factura #{factura.id}"
            )

        # Recalcular totales
        factura.recalcular_totales()

        # Preparar detalles con información de productos para el template
        detalles_para_email = []
        for detalle in factura.detalles.all():
            detalles_para_email.append({
                "descripcion": detalle.descripcion,
                "producto_nombre": detalle.producto.nombre if detalle.producto else None,
                "cantidad": detalle.cantidad,
                "precio_unitario": float(detalle.precio_unitario),
                "subtotal": float(detalle.subtotal)
            })

        # Enviar email de factura de venta directa (template específico)
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        context = {
            "cliente_nombre": factura.cliente.get_full_name(),
            "factura_id": factura.id,
            "fecha_emision": factura.fecha.strftime("%d/%m/%Y %H:%M"),
            "estado": factura.estado,
            "subtotal": float(factura.subtotal),
            "impuestos": float(factura.impuestos),
            "total": float(factura.total),
            "detalles": detalles_para_email,
            "url_historial": f"{frontend_url}/app/facturacion/{factura.id}",
            "anio_actual": datetime.now().year,
        }

        FacturaVentaDirectaEmail(context, factura.cliente.email).send()

        return factura
    
    
    @staticmethod
    def pagar_factura(factura_id, metodo_pago, monto, referencia=""):
        factura = Factura.objects.get(id=factura_id)

        pago = Pago.objects.create(
            factura=factura,
            metodo=metodo_pago,    # Aquí ya es MetodoPago
            monto=monto,
            referencia=referencia
        )

        if factura.estado == "PAGADA":
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
            context = {
                "cliente_nombre": factura.cliente.get_full_name(),
                "factura_id": factura.id,
                "total": factura.total,
                "metodo_pago": pago.metodo.nombre,  
                "fecha_pago": pago.fecha.strftime("%d/%m/%Y %H:%M"),  
                "detalles": factura.detalles.all(),
                "url_historial": f"{frontend_url}/app/facturacion/{factura.id}",
                "anio_actual": datetime.now().year,
            }

            FacturaPagadaEmail(context, factura.cliente.email).send()

        return factura
    

    @staticmethod
    def anular_factura(factura_id):
        factura = Factura.objects.get(id=factura_id)
        estado = EstadoFacturaFactory.obtener_estado(factura.estado)

        # Aplicar lógica de cambio de estado
        estado.anular(factura)

        return factura