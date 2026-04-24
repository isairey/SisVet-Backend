# notificaciones/patterns/strategies/strategy_consulta.py

from ..template_method import BaseNotification


class ConsultaConsentimientoEmail(BaseNotification):
    """Notificación para solicitar consentimiento"""

    def get_subject(self) -> str:
        return "Solicitud de Consentimiento - Consulta Veterinaria"

    def get_template_name(self) -> str:
        return "emails/consulta_consentimiento.html"

# (Aquí también puedes añadir la clase ConsultaFinalizadaEmail si la necesitas)