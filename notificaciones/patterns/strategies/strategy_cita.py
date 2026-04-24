"""
clases concretas que heredan del molde  son las "estrategias" de notificación
Su única responsabilidad es definir el contenido (subject y template_name).
"""
# notificaciones/patterns/strategies/strategy_cita.py

from ..template_method import BaseNotification 

"""
Define las estrategias de notificación concretas
exclusivamente para el dominio de CITAS.
"""

class CitaAgendadaEmail(BaseNotification):
    """Notificación concreta para Cita Agendada (RF-004)."""
    
    def get_subject(self) -> str:
        return "¡Tu cita ha sido agendada!"
    
    def get_template_name(self) -> str:
        return "emails/cita_agendada.html"

class CitaCanceladaEmail(BaseNotification):
    """Notificación concreta para Cita Cancelada (RF-007)."""
    
    def get_subject(self) -> str:
        return "Tu cita ha sido cancelada"
    
    def get_template_name(self) -> str:
        return "emails/cita_cancelada.html"

class CitaReagendadaEmail(BaseNotification):
    """Notificación concreta para Cita Reagendada (RF-006)."""
    
    def get_subject(self) -> str:
        return "¡Tu cita ha sido reagendada!"
    
    def get_template_name(self) -> str:
        return "emails/cita_reagendada.html"