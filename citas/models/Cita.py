from django.db import models
from common.models import BaseModel 
from usuarios.models import Usuario 
from mascotas.models import Mascota 
from citas.models import Servicio 
from citas.patterns.state import EstadoCita

class Cita(BaseModel):
    """
    Modelo principal de Citas.
    Su responsabilidad es la ESTRUCTURA de datos.
    La lógica de su estado se importa desde 'choices.py'.
    """

    # --- Relaciones ---
    mascota = models.ForeignKey(
        Mascota, 
        on_delete=models.CASCADE, 
        related_name='citas'
    )
    
    veterinario = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='citas_como_veterinario',
        # Filtro para que aquí SOLO se puedan asignar Veterinarios o Practicantes
        limit_choices_to=models.Q(usuario_roles__rol__nombre='veterinario') | models.Q(usuario_roles__rol__nombre='practicante')
    )
    
    servicio = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True)

    # --- Campos de Datos ---
    fecha_hora = models.DateTimeField()
    
    # Este campo usa nuestro Patrón State consumiendo la lógica de 'choices.py'
    estado = models.CharField(
        max_length=20,
        choices=EstadoCita.CHOICES,
        default=EstadoCita.AGENDADA 
    )
    
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['fecha_hora']

    def __str__(self):
        return f"Cita de {self.mascota.nombre} - {self.fecha_hora}"