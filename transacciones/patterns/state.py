from abc import ABC, abstractmethod

class EstadoFactura(ABC):

    @abstractmethod
    def pagar(self, factura):
        pass

    @abstractmethod
    def anular(self, factura):
        pass


class FacturaPendiente(EstadoFactura):

    def pagar(self, factura):
        factura.estado = 'PAGADA'
        factura.save()

    def anular(self, factura):
        factura.estado = 'ANULADA'
        factura.save()


class FacturaPagada(EstadoFactura):

    def pagar(self, factura):
        raise ValueError("La factura ya está pagada.")

    def anular(self, factura):
        raise ValueError("No puedes anular una factura pagada.")


class FacturaAnulada(EstadoFactura):

    def pagar(self, factura):
        raise ValueError("No puedes pagar una factura anulada.")

    def anular(self, factura):
        raise ValueError("La factura ya está anulada.")