from datetime import time
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied
from citas.models import Cita
from citas.patterns.state import EstadoCita
from citas.patterns.state.state_factory import EstadoCitaFactory
from citas.patterns.composite import AgendaDiaria, BloqueTurno
from citas.signals import cita_reagendada_signal
from usuarios.models import Usuario
from .interface import ICommand
from .utils import parsear_fecha_hora

class ReagendarCitaCommand(ICommand):
    def __init__(self, cita_id: int, nueva_fecha_str: str, usuario: Usuario):
        self.cita_id = cita_id
        self.nueva_fecha_str = nueva_fecha_str
        self.usuario = usuario

    def execute(self) -> Cita:
        try:
            cita = Cita.objects.get(id=self.cita_id)
        except Cita.DoesNotExist:
            raise ValidationError("La cita no existe.")

        # 1. Permisos
        es_propietario = cita.mascota.cliente.usuario == self.usuario
        es_admin = self.usuario.usuario_roles.filter(
            rol__nombre__in=['recepcionista', 'administrador']
        ).exists()

        if not es_propietario and not es_admin:
            raise PermissionDenied("No tienes permiso para reagendar esta cita.")

        # 2. Parseo y Validación de Fecha
        nueva_fecha = parsear_fecha_hora(self.nueva_fecha_str)

        if nueva_fecha < timezone.now():
             raise ValidationError("No se puede reagendar al pasado.")

        # --- LÓGICA DE DISPONIBILIDAD (Patrón Composite) ---
        
        # a. Obtener citas ocupadas en la NUEVA fecha
        # IMPORTANTE: Excluimos la cita actual para evitar falsos positivos si se mueve dentro del mismo día
        citas_ocupadas = Cita.objects.filter(
            veterinario_id=cita.veterinario.id,
            fecha_hora__date=nueva_fecha.date()
        ).exclude(
            id=cita.id  # <--- Excluir la cita que estamos moviendo
        ).exclude(
            estado=EstadoCita.CANCELADA
        ).values_list('fecha_hora', flat=True)
        
        horarios_ocupados_set = {
            c.astimezone(timezone.get_current_timezone()).time() 
            for c in citas_ocupadas
        }

        # b. Construir Agenda y Verificar
        agenda = AgendaDiaria()
        agenda.agregar(BloqueTurno(time(8, 0), time(12, 0)))
        agenda.agregar(BloqueTurno(time(14, 0), time(18, 0)))
        
        horarios_libres = agenda.obtener_cupos_libres(nueva_fecha.date(), horarios_ocupados_set)

        nueva_fecha_local = nueva_fecha.astimezone(timezone.get_current_timezone())

        if nueva_fecha_local.strftime("%H:%M") not in horarios_libres:
            raise ValidationError("El veterinario no está disponible en el nuevo horario solicitado.")

        # 3. Delegar al Estado (Patrón State)
        # La fábrica instancia el estado actual (ej. AgendadaState) y este valida si puede transicionar
        estado_actual = EstadoCitaFactory.obtener_estado(cita.estado)
        estado_actual.reagendar(cita, nueva_fecha) 

        # 4. Notificar (Signal)
        cita_reagendada_signal.send(sender=Cita, cita=cita)
        
        return cita