"""
Su única responsabilidad es orquestar el proceso: 
tomar la solicitud, pasársela a la fábrica y decirle al objeto resultante que se envíe.
"""

# Importamos solo la Fábrica de nuestro paquete de patrones
from .patterns.factory import NotificationFactory

def enviar_notificacion_generica(evento: str, context: dict, to_email: str):
    """
    Servicio principal de notificaciones (Orquestador).
    
    Su única responsabilidad es coordinar la creación y el envío
    de una notificación.
    """
    try:
        # 1. Solicita a la Fábrica que construya la notificación
        notificacion = NotificationFactory.get_notification(
            evento, 
            context, 
            to_email
        )
        
        # 2. Le dice a la notificación que se envíe (usando su Template Method)
        notificacion.send()
        
    except ValueError as e:
        # Evento desconocido
        print(e)
    except Exception as e:
        # Error general (ej: SMTP, plantilla no encontrada)
        print(f"Error crítico en el servicio de notificación: {e}")