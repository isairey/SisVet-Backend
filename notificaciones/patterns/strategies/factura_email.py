from ..template_method import BaseNotification

class FacturaGeneradaEmail(BaseNotification):
    def get_subject(self) -> str:
        return f"Factura #{self.context_data.get('factura_id')} generada"

    def get_template_name(self) -> str:
        return "emails/factura_generada.html"


class FacturaPagadaEmail(BaseNotification):
    def get_subject(self) -> str:
        return f"Factura #{self.context_data.get('factura_id')} pagada"

    def get_template_name(self) -> str:
        return "emails/factura_pagada.html"


class FacturaEnvioManualEmail(BaseNotification):
    def get_subject(self) -> str:
        return f"Factura #{self.context_data.get('factura_id')}"

    def get_template_name(self) -> str:
        return "emails/factura_manual.html"


class FacturaVentaDirectaEmail(BaseNotification):
    """
    Estrategia de notificación para facturas generadas por venta directa de productos.
    Usa un template específico para este tipo de factura.
    """
    def get_subject(self) -> str:
        return f"Factura #{self.context_data.get('factura_id')} generada"

    def get_template_name(self) -> str:
        return "emails/factura_venta_directa.html"