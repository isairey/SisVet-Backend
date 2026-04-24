"""
inventario/apps.py

Configuración de la aplicación de inventario.
Registra los signals y patrones al iniciar Django.
"""
from django.apps import AppConfig


class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventario'
    verbose_name = 'Gestión de Inventario'

    def ready(self):
        """
        Se ejecuta cuando Django inicializa la app.

        Responsabilidades:
        1. Importar signals (para registrarlos automáticamente)
        2. Inicializar patrones (Observer, Singleton)
        """
        # Importar signals para registrarlos
        import inventario.signals.kardex_signals

        # Inicializar Observer Pattern
        from inventario.patrones import obtener_sujeto_inventario
        obtener_sujeto_inventario()

        # Inicializar Singleton Pattern
        from inventario.patrones import GestorInventario
        GestorInventario()