from django.db import models
from common.models import BaseModel
from usuarios.models import Usuario
from mascotas.models import Mascota # ¡Importamos nuestra maqueta!

class Servicio(BaseModel):
    """
    Define los servicios de la clínica (RF-004).
    Capa de Datos.
    """
    nombre = models.CharField(max_length=100, unique=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.nombre

class Cita(BaseModel):
    """
    Modelo principal de Citas. Implementa Patrón State.
    Relaciona Mascota, Veterinario (Usuario) y Servicio.
    Capa de Datos.
    """

    # --- Implementación de Patrón State ---
    # Definimos los únicos estados posibles para la cita
    ESTADO_AGENDADA = 'AGENDADA'
    ESTADO_CANCELADA = 'CANCELADA'
    ESTADO_COMPLETADA = 'COMPLETADA'

    ESTADO_CHOICES = [
        (ESTADO_AGENDADA, 'Agendada'),
        (ESTADO_CANCELADA, 'Cancelada'),
        (ESTADO_COMPLETADA, 'Completada'),
    ]
    # ------------------------------------

    # --- Relaciones  ---
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)

    # Conectamos al modelo Usuario, pero filtramos para que solo
    # se puedan seleccionar usuarios que sean 'veterinario' o 'practicante'.
    veterinario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='citas_como_veterinario',
        limit_choices_to={'usuario_roles__rol__nombre__in': ['veterinario', 'practicante']}
    )

    servicio = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True)

    # --- Campos de la Cita ---
    fecha_hora = models.DateTimeField()

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_AGENDADA # <-- Patrón State: estado inicial
    )

    # (El campo 'propietario' no es necesario aquí,
    # ya que lo podemos obtener a través de la mascota: cita.mascota.propietario)

    class Meta:
        ordering = ['fecha_hora'] # Ordena las citas por fecha

    def __str__(self):
        return f"Cita de {self.mascota.nombre} - {self.fecha_hora}"