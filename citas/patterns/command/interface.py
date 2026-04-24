from abc import ABC, abstractmethod

class ICommand(ABC):
    """Interfaz base para todos los comandos de citas."""
    
    @abstractmethod
    def execute(self):
        """Ejecuta la lógica del comando y retorna el resultado (opcional)."""
        pass