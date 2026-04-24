# notificaciones/strategies/verify_account_email.py
from ..template_method import BaseNotification

class VerifyAccountEmail(BaseNotification):
    """
    Estrategia de notificación para el envío del código de verificación de cuenta.
    Hereda de BaseNotification (Template Method).
    """
    
    def get_subject(self) -> str:
        """Define el asunto del correo."""
        return "Verifica tu Cuenta en SGV - Código de Acceso"

    def get_template_name(self) -> str:
        """Define el nombre del template HTML a usar."""
        # Usamos el nombre de template que proporcionaste
        return "emails/email_verification_template.html" 

    def get_from_email(self) -> str:
        """Opcional: Define el remitente. Si no se implementa, usa DEFAULT_FROM_EMAIL."""
        # Se puede dejar así para usar el valor de settings.py
        return super().get_from_email()