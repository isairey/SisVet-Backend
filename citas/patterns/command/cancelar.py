from rest_framework.exceptions import ValidationError, PermissionDenied
from citas.models import Cita
from citas.signals import cita_cancelada_signal
from usuarios.models import Usuario
from citas.patterns.state.state_factory import EstadoCitaFactory  # Importamos la fábrica
from .interface import ICommand

class CancelarCitaCommand(ICommand):
    def __init__(self, cita_id: int, usuario: Usuario):
        self.cita_id = cita_id
        self.usuario = usuario

    def execute(self) -> Cita:
        try:
            cita = Cita.objects.get(id=self.cita_id)
        except Cita.DoesNotExist:
            raise ValidationError("La cita no existe.")

        # 1. Validar Permisos (Esto sigue siendo responsabilidad del comando)
        es_propietario = cita.mascota.cliente.usuario == self.usuario
        es_admin_o_vet = self.usuario.usuario_roles.filter(
            rol__nombre__in=['recepcionista', 'administrador', 'veterinario']
        ).exists()

        if not es_propietario and not es_admin_o_vet:
            raise PermissionDenied("No tienes permiso para cancelar esta cita.")

        # 2. Delegar la lógica de transición al Estado (Refactorización clave)
        estado_actual = EstadoCitaFactory.obtener_estado(cita.estado)
        estado_actual.cancelar(cita)  # <- Aquí ocurre la magia polimórfica

        # 3. Notificar
        cita_cancelada_signal.send(sender=Cita, cita=cita)
        return cita