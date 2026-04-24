from django.apps import AppConfig


class TransaccionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transacciones'

    def ready(self):
        # importa señales para que se registren
        import transacciones.models.signals  # noqa
