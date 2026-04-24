# notificaciones/handlers/handler_consulta.py

from django.dispatch import receiver
from consultas.signals import consulta_consentimiento_signal # 1. Importa la señal
from consultas.models import Consulta
from ..services import enviar_notificacion_generica
from ._helpers import preparar_contexto_consulta

@receiver(consulta_consentimiento_signal)
def handle_consulta_consentimiento(sender, consulta: Consulta, **kwargs):
    """
    Escucha la señal 'consulta_consentimiento_signal' y envía el email.
    """
    print(f"--- 📣 [Handler Consulta] Señal CONSENTIMIENTO recibida para {consulta.id} ---")
    try:
        context = preparar_contexto_consulta(consulta) # Usamos el helper
        if context:
            enviar_notificacion_generica(
                evento="CONSULTA_CONSENTIMIENTO", # Llama a la Factory
                context=context,
                to_email=context.get('to_email')
            )
    except Exception as e:
        print(f"Error en handler de CONSENTIMIENTO: {e}")

# (Aquí también puedes añadir el handler para 'consulta_finalizada_signal' si lo deseas)