# apps/consultas/services/consentimiento_service.py

import secrets
from consultas.signals import consulta_consentimiento_signal

def generar_token():
    return secrets.token_urlsafe(32)

def enviar_consentimiento(consulta):
    """
    Setea token + reinicia estado + dispara signal.
    """
    token = generar_token()

    consulta.consentimiento_token = token
    consulta.consentimiento_otorgado = False
    consulta.save(update_fields=["consentimiento_token", "consentimiento_otorgado"])

    # Disparo de signal
    consulta_consentimiento_signal.send(sender=consulta.__class__, consulta=consulta)

    return token
