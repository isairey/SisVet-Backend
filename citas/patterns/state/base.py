from abc import ABC, abstractmethod

class EstadoCita(ABC):
    """
    Clase base abstracta y contenedor de constantes para los estados de una cita.
    """
    
    # --- Constantes para el Modelo (Persistencia) ---
    AGENDADA = 'AGENDADA'
    EN_PROGRESO = 'EN_PROGRESO' # Nuevo Estado SSOT
    CANCELADA = 'CANCELADA'
    COMPLETADA = 'COMPLETADA'

    CHOICES = [
        (AGENDADA, 'Agendada'),
        (EN_PROGRESO, 'En Progreso'),
        (CANCELADA, 'Cancelada'),
        (COMPLETADA, 'Completada'),
    ]

    # --- Contrato de Comportamiento (Patrón State) ---
    
    @abstractmethod
    def cancelar(self, cita):
        pass

    @abstractmethod
    def reagendar(self, cita, nueva_fecha):
        pass

    @abstractmethod
    def completar(self, cita):
        pass

    @abstractmethod
    def iniciar(self, cita): # Nuevo método de transición
        pass