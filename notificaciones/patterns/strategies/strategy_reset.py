from ..template_method import BaseNotification


class ResetPasswordEmail(BaseNotification):
    """Estrategia de notificación para solicitar restablecimiento de contraseña."""
    
    def get_subject(self) -> str:
        return "Restablece tu contraseña"

    def get_template_name(self) -> str:
        return "emails/reset_password.html"


class PasswordResetSuccessEmail(BaseNotification):
    """Estrategia de notificación para confirmar que la contraseña fue restablecida exitosamente."""
    
    def get_subject(self) -> str:
        return "Contraseña restablecida exitosamente - SGV"

    def get_template_name(self) -> str:
        return "emails/password_reset_success.html"
