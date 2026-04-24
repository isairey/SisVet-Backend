from datetime import datetime, time
from django.utils import timezone
from citas.models import Cita
from citas.patterns.state import EstadoCita
from citas.patterns.composite import AgendaDiaria, BloqueTurno

class DisponibilidadService:
    """
    Orquestador de Lógica de Negocio para Disponibilidad.
    Responsabilidad: 
    1. Buscar datos en DB.
    2. Instanciar el Patrón Composite.
    3. Devolver resultados a la Vista.
    """

    def calcular_horarios_disponibles(self, veterinario_id: int, fecha: datetime.date) -> list[str]:
        # 1. Obtener Citas Ocupadas de la BD (Capa de Datos)
        # Filtramos citas que NO estén canceladas (usando string por ahora, luego el patrón State)
        citas_ocupadas = Cita.objects.filter(
            veterinario_id=veterinario_id,
            fecha_hora__date=fecha
        ).exclude(
            estado=EstadoCita.CANCELADA
        ).values_list('fecha_hora', flat=True)

        # Convertimos a un set de objetos time para búsqueda rápida O(1)
        # Nota: Ajustamos la zona horaria para comparar correctamente
        horarios_ocupados_set = {
            c.astimezone(timezone.get_current_timezone()).time() 
            for c in citas_ocupadas
        }

        # 2. Construir la estructura del Patrón Composite (Lógica de Negocio)
        # Aquí definimos las reglas: El veterinario trabaja mañana y tarde.
        agenda_composite = AgendaDiaria()
        
        # Turno Mañana: 08:00 - 12:00
        turno_manana = BloqueTurno(hora_inicio=time(8, 0), hora_fin=time(12, 0))
        
        # Turno Tarde: 14:00 - 18:00 (Hueco de 2h para almuerzo implícito)
        turno_tarde = BloqueTurno(hora_inicio=time(14, 0), hora_fin=time(18, 0))

        agenda_composite.agregar(turno_manana)
        agenda_composite.agregar(turno_tarde)

        # 3. Ejecutar el algoritmo del patrón
        return agenda_composite.obtener_cupos_libres(fecha, horarios_ocupados_set)