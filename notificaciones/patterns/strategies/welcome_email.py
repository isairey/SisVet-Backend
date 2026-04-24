# notificaciones/strategies/welcome_email.py
from ..template_method import BaseNotification

class WelcomeEmail(BaseNotification):
    """
    Estrategia de notificación para el correo de bienvenida después de verificar la cuenta.
    Hereda de BaseNotification (Template Method).
    """
    
    def get_subject(self) -> str:
        """Define el asunto del correo."""
        return "¡Bienvenido a SGV - Tu cuenta está verificada!"

    def get_template_name(self) -> str:
        """Define el nombre del template HTML a usar."""
        return "emails/welcome_email.html"

