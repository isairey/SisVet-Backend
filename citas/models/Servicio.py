from django.db import models
from common.models import BaseModel 
from usuarios.models import Usuario 
from mascotas.models import Mascota 

class Servicio(BaseModel):
    """
    Define los servicios de la clínica (RF-004).
    Ej: "Consulta General", "Vacunación", "Fractura".
    """
    nombre = models.CharField(max_length=100, unique=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.nombre