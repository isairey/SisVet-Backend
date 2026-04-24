from usuarios.models import Usuario
from citas.patterns.command import AgendarCitaCommand, CancelarCitaCommand, ReagendarCitaCommand

def ejecutar_agendamiento(data: dict, usuario: Usuario):
    comando = AgendarCitaCommand(data, usuario)
    return comando.execute()

def ejecutar_cancelacion(cita_id: int, usuario: Usuario):
    comando = CancelarCitaCommand(cita_id, usuario)
    return comando.execute()

def ejecutar_reagendamiento(cita_id: int, nueva_fecha: str, usuario: Usuario):
    comando = ReagendarCitaCommand(cita_id, nueva_fecha, usuario)
    return comando.execute()