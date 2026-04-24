from .state import FacturaPendiente, FacturaPagada, FacturaAnulada

class EstadoFacturaFactory:

    @staticmethod
    def obtener_estado(estado):
        if estado == 'PENDIENTE':
            return FacturaPendiente()
        if estado == 'PAGADA':
            return FacturaPagada()
        if estado == 'ANULADA':
            return FacturaAnulada()
        raise ValueError("Estado de factura no válido.")