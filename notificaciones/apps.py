from django.apps import AppConfig

class NotificacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notificaciones'

    def ready(self):
        """
        Esta función importa los manejadores de señales para registrarlos.
        """
        try:
            # Importamos el handler específico de citas
            import notificaciones.handlers.handler_cita
            # Importamos el handler específico de consultas
            import notificaciones.handlers.handler_consulta
            
        except ImportError:
            pass