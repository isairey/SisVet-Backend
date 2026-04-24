from .template_method import BaseNotification
# Importamos desde nuestra subcarpeta de estrategias
from .strategies.strategy_cita import (CitaAgendadaEmail,CitaCanceladaEmail,CitaReagendadaEmail)
from .strategies.strategy_consulta import ConsultaConsentimientoEmail
from .strategies.strategy_reset import ResetPasswordEmail, PasswordResetSuccessEmail
from .strategies.verify_account_email import VerifyAccountEmail
from .strategies.welcome_email import WelcomeEmail
# Futuro: 
# from .strategies.strategy_consulta import ConsultaFinalizadaEmail

"""
Implementa el Patrón Factory Method.
"""

class NotificationFactory:
    """
    Fábrica que decide qué tipo de notificación construir
    basado en un "evento".
    Su única responsabilidad es la "creación" del objeto correcto.
    """
    
    @staticmethod
    def get_notification(evento: str, context: dict, to_email: str) -> BaseNotification:
        """
        El método "Factory".
        """
        
        # Mapeamos el string del evento a la Clase constructora
        estrategias = {
            # --- Eventos de Citas ---
            "CITA_CREADA": CitaAgendadaEmail,
            "CITA_CANCELADA": CitaCanceladaEmail,
            "CITA_REAGENDADA": CitaReagendadaEmail,

            "CONSULTA_CONSENTIMIENTO": ConsultaConsentimientoEmail,
            
            # --- Eventos de Consultas (Futuro) ---
            # "CONSULTA_FINALIZADA": ConsultaFinalizadaEmail, 
            # --- Eventos de Reset Password ---
            "RESET_PASSWORD": ResetPasswordEmail,
            "PASSWORD_RESET_SUCCESS": PasswordResetSuccessEmail,
            "VERIFY_ACCOUNT_EMAIL": VerifyAccountEmail,
            # --- Eventos de Bienvenida ---
            "WELCOME_EMAIL": WelcomeEmail,
        }

        ConstructorDeNotificacion = estrategias.get(evento)

        if ConstructorDeNotificacion:
            return ConstructorDeNotificacion(context, to_email)
        else:
            raise ValueError(f"Evento de notificación desconocido: {evento}")