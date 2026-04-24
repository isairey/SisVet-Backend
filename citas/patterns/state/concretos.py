from rest_framework.exceptions import ValidationError
from .base import EstadoCita

class EstadoAgendada(EstadoCita):
    def cancelar(self, cita):
        cita.estado = EstadoCita.CANCELADA
        cita.save()

    def reagendar(self, cita, nueva_fecha):
        cita.fecha_hora = nueva_fecha
        cita.estado = EstadoCita.AGENDADA 
        cita.save()

    def completar(self, cita):
        # Permitimos completar directamente o exigimos pasar por progreso (regla de negocio)
        # Asumiremos que se puede completar directamente si fue rápida
        cita.estado = EstadoCita.COMPLETADA
        cita.save()
        
    def iniciar(self, cita):
        # Transición válida: Agendada -> En Progreso
        cita.estado = EstadoCita.EN_PROGRESO
        cita.save()


class EstadoEnProgreso(EstadoCita):
    """
    Representa una cita que está ocurriendo en este momento.
    """
    def cancelar(self, cita):
        # Depende de la regla de negocio. Generalmente si ya empezó, no se cancela, se completa o se abandona.
        # Aquí asumiremos que se puede cancelar si hubo un error al iniciarla.
        cita.estado = EstadoCita.CANCELADA
        cita.save()

    def reagendar(self, cita, nueva_fecha):
        raise ValidationError("No se puede reagendar una cita que ya está en curso. Debe finalizarla primero.")

    def completar(self, cita):
        # Transición natural: En Progreso -> Completada
        cita.estado = EstadoCita.COMPLETADA
        cita.save()

    def iniciar(self, cita):
        raise ValidationError("La cita ya está en progreso.")


class EstadoCancelada(EstadoCita):
    def cancelar(self, cita):
        raise ValidationError("Esta cita ya ha sido cancelada previamente.")
    def reagendar(self, cita, nueva_fecha):
        raise ValidationError("No se puede reagendar una cita cancelada. Debe crear una nueva.")
    def completar(self, cita):
        raise ValidationError("No se puede completar una cita cancelada.")
    def iniciar(self, cita):
        raise ValidationError("No se puede iniciar una cita cancelada.")


class EstadoCompletada(EstadoCita):
    def cancelar(self, cita):
        raise ValidationError("No se puede cancelar una cita que ya fue completada.")
    def reagendar(self, cita, nueva_fecha):
        raise ValidationError("No se puede reagendar una cita completada.")
    def completar(self, cita):
        raise ValidationError("La cita ya está marcada como completada.")
    def iniciar(self, cita):
        raise ValidationError("La cita ya finalizó.")