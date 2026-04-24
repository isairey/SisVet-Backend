from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied

from citas.models import Cita, Servicio
from mascotas.models import Mascota
from usuarios.models import Usuario
from citas.patterns.state.base import EstadoCita 
from citas.patterns.composite import AgendaDiaria, BloqueTurno 
from citas.signals import cita_agendada_signal

from .interface import ICommand
from .utils import parsear_fecha_hora

class AgendarCitaCommand(ICommand):
    def __init__(self, data: dict, usuario: Usuario):
        self.data = data
        self.usuario = usuario

    def execute(self) -> Cita:
        mascota_id = self.data.get('mascota_id')
        veterinario_id = self.data.get('veterinario_id')
        servicio_id = self.data.get('servicio_id')
        fecha_hora_input = self.data.get('fecha_hora')

        # 1. Helper
        fecha_hora = parsear_fecha_hora(fecha_hora_input)

        # 2. Validaciones
        try:
            mascota = Mascota.objects.get(id=mascota_id)
            veterinario = Usuario.objects.get(id=veterinario_id)
            servicio = Servicio.objects.get(id=servicio_id)
        except (Mascota.DoesNotExist, Usuario.DoesNotExist, Servicio.DoesNotExist):
            raise ValidationError("La mascota, veterinario o servicio no existen.")

        self._verificar_permisos(mascota)

        if fecha_hora < timezone.now():
            raise ValidationError("No se pueden agendar citas en el pasado.")

        # --- LÓGICA DE DISPONIBILIDAD (Composite) ---
        # Replicamos la lógica del servicio para validar, o llamamos al servicio.
        # Para evitar dependencias circulares (Service -> Command -> Service),
        # usaremos el patrón Composite directamente aquí.
        
        # a. Obtener citas ocupadas
        citas_ocupadas = Cita.objects.filter(
            veterinario_id=veterinario.id,
            fecha_hora__date=fecha_hora.date()
        ).exclude(
            estado=EstadoCita.CANCELADA
        ).values_list('fecha_hora', flat=True)
        
        horarios_ocupados_set = {
            c.astimezone(timezone.get_current_timezone()).time() 
            for c in citas_ocupadas
        }

        # b. Usar Composite
        from datetime import time
        agenda = AgendaDiaria()
        agenda.agregar(BloqueTurno(time(8, 0), time(12, 0)))
        agenda.agregar(BloqueTurno(time(14, 0), time(18, 0)))
        
        horarios_libres = agenda.obtener_cupos_libres(fecha_hora.date(), horarios_ocupados_set)

        fecha_hora_local = fecha_hora.astimezone(timezone.get_current_timezone())

        if fecha_hora_local.strftime("%H:%M") not in horarios_libres:
            raise ValidationError(f"El veterinario no está disponible a las {fecha_hora.strftime('%H:%M')}.")

        # 3. Ejecución
        cita = Cita.objects.create(
            mascota=mascota,
            veterinario=veterinario,
            servicio=servicio,
            fecha_hora=fecha_hora,
            observaciones=self.data.get('observaciones', ''),
            estado=EstadoCita.AGENDADA
        )

        cita_agendada_signal.send(sender=Cita, cita=cita)
        return cita

    def _verificar_permisos(self, mascota):
        if hasattr(self.usuario, 'perfil_cliente'):
             if mascota.cliente.usuario != self.usuario:
                raise PermissionDenied("No tienes permiso para esta mascota.")