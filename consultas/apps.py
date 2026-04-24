"""
apps.py
Configuración principal de la aplicación Consultas.
Sara Sánchez
03 noviembre2025
"""

from django.apps import AppConfig
from importlib import import_module


class ConsultasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'consultas'
    verbose_name = 'Gestión de Consultas y Historias Clínicas'

    def ready(self):
        """
        Se ejecuta automáticamente cuando Django inicia la app.
        """
        # Importa los signals para que se registren correctamente al iniciar la app
        try:
            import_module(f"{self.name}.signals")
        except Exception:
            # No interrumpe la carga del sistema si no existen todavía
            pass