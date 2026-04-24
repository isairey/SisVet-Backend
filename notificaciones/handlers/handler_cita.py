from django.dispatch import receiver
from citas.signals import cita_agendada_signal, cita_cancelada_signal, cita_reagendada_signal
from citas.models import Cita
from ..services import enviar_notificacion_generica # 2. Llama al servicio
from ._helpers import preparar_contexto_cita      # 3. Usa el helper

"""
Responsabilidad Única: Manejar (escuchar) todas las señales
relacionadas con el dominio de CITAS.
"""

@receiver(cita_agendada_signal)
def handle_cita_agendada(sender, cita: Cita, **kwargs):
    """Escucha la señal 'cita_agendada_signal' y delega al servicio."""
    
    print(f"--- 📣 [Handler Cita] Señal CITA_CREADA recibida para {cita.id} ---")
    try:
        context = preparar_contexto_cita(cita)
        if context:
            enviar_notificacion_generica(
                evento="CITA_CREADA",
                context=context,
                to_email=context.get('to_email')
            )
    except Exception as e:
        print(f"Error en handler de CITA_CREADA: {e}")

@receiver(cita_cancelada_signal)
def handle_cita_cancelada(sender, cita: Cita, **kwargs):
    """Escucha la señal 'cita_cancelada_signal' y delega al servicio."""
    
    print(f"--- 📣 [Handler Cita] Señal CITA_CANCELADA recibida para {cita.id} ---")
    try:
        context = preparar_contexto_cita(cita)
        if context:
            enviar_notificacion_generica(
                evento="CITA_CANCELADA",
                context=context,
                to_email=context.get('to_email')
            )
    except Exception as e:
        print(f"Error en handler de CITA_CANCELADA: {e}")

@receiver(cita_reagendada_signal)
def handle_cita_reagendada(sender, cita: Cita, **kwargs):
    """Escucha la señal 'cita_reagendada_signal' y delega al servicio."""
    
    print(f"--- 📣 [Handler Cita] Señal CITA_REAGENDADA recibida para {cita.id} ---")
    try:
        context = preparar_contexto_cita(cita)
        if context:
            enviar_notificacion_generica(
                evento="CITA_REAGENDADA",
                context=context,
                to_email=context.get('to_email')
            )
    except Exception as e:
        print(f"Error en handler de CITA_REAGENDADA: {e}")