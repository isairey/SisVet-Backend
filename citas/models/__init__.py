# Esto hace que Django "vea" tus modelos aunque estén en archivos separados
from citas.models.Servicio import Servicio
from citas.models.Cita import Cita

__all__ = ['Servicio', 'Cita']