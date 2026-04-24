from abc import ABC, abstractmethod
from datetime import datetime, timedelta, time

class ComponenteTemporal(ABC):
    """
    Componente (Interfaz): Define el comportamiento común para
    bloques de tiempo y agendas compuestas.
    """
    
    @abstractmethod
    def obtener_cupos_libres(self, fecha: datetime.date, horarios_ocupados: set) -> list[str]:
        """
        Retorna una lista de horas (strings 'HH:MM') disponibles,
        excluyendo los horarios que estén en el set 'horarios_ocupados'.
        """
        pass

    @abstractmethod
    def agregar(self, componente: 'ComponenteTemporal'):
        pass


class BloqueTurno(ComponenteTemporal):
    """
    Hoja (Leaf): Representa un turno continuo (ej: 08:00 a 12:00).
    Es la unidad indivisible que genera los slots de tiempo.
    """

    def __init__(self, hora_inicio: time, hora_fin: time, intervalo_minutos: int = 30):
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.intervalo = timedelta(minutes=intervalo_minutos)

    def agregar(self, componente: ComponenteTemporal):
        # Una hoja no puede tener hijos
        raise NotImplementedError("No se pueden agregar componentes a un bloque hoja.")

    def obtener_cupos_libres(self, fecha: datetime.date, horarios_ocupados: set) -> list[str]:
        cupos = []
        
        # Convertimos a datetime completo para poder sumar el timedelta
        actual = datetime.combine(fecha, self.hora_inicio)
        fin = datetime.combine(fecha, self.hora_fin)
        ahora = datetime.now()

        while actual < fin:
            # Lógica de negocio básica: No mostrar horas pasadas si es hoy
            if actual > ahora:
                hora_str = actual.time().strftime("%H:%M") # "08:00"
                hora_obj = actual.time() # objeto time

                # Verificamos si esta hora específica está ocupada (Composite logic)
                if hora_obj not in horarios_ocupados:
                    cupos.append(hora_str)
            
            actual += self.intervalo
            
        return cupos


class AgendaDiaria(ComponenteTemporal):
    """
    Compuesto (Composite): Representa la agenda de un día.
    Se compone de múltiples BloqueTurno (ej: Mañana y Tarde).
    """

    def __init__(self):
        self._componentes = []

    def agregar(self, componente: ComponenteTemporal):
        self._componentes.append(componente)

    def obtener_cupos_libres(self, fecha: datetime.date, horarios_ocupados: set) -> list[str]:
        todos_los_cupos = []
        # Delega la tarea a cada turno (hijo) y concatena los resultados
        for componente in self._componentes:
            cupos_turno = componente.obtener_cupos_libres(fecha, horarios_ocupados)
            todos_los_cupos.extend(cupos_turno)
        
        return todos_los_cupos