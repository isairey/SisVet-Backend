# Importamos los "observadores" concretos de nuestra nueva app
from notificaciones.services import CitaAgendadaEmail,  CitaCanceladaEmail, CitaReagendadaEmail
from citas.models import Cita

# Importamos los modelos necesarios para la optimización
from usuarios.models import Usuario
from mascotas.models import Mascota, Cliente

def notificar_observadores(evento: str, cita: Cita):
    """
    Implementación del Patrón Observer (el "Notificador").
    Dispara el servicio de notificación correspondiente basado en el evento.
    
    Args:
        evento (str): El tipo de evento (ej: "CITA_CREADA").
        cita (Cita): La instancia de la cita que cambió.
    """
    try:
        # Optimizamos la consulta: le decimos a Django que traiga
        # todos los datos relacionados que el email necesitará en una
        # sola consulta a la base de datos.
        cita_con_datos = Cita.objects.select_related(
            'mascota__cliente__usuario', # Ruta corregida
            'veterinario', 
            'servicio'
        ).get(id=cita.id)

        print(f"--- OBSERVADOR: Evento '{evento}' detectado para Cita {cita.id} ---")

        # Aquí, el "Observador" decide qué "Sub-Observador" llamar
        if evento == "CITA_CREADA":
            CitaAgendadaEmail(cita_con_datos).send()

        elif evento == "CITA_CANCELADA":
            CitaCanceladaEmail(cita_con_datos).send()

        elif evento == "CITA_REAGENDADA":
            CitaReagendadaEmail(cita_con_datos).send()

        print("--- Notificación enviada ---")

    except Cita.DoesNotExist:
        print(f"Error de Observador: No se encontró la Cita {cita.id} para notificar.")
    except Exception as e:
        # Captura cualquier error (ej. SMTP) para no detener la creación de la cita
        print(f"Error fatal en el sistema de notificación: {e}")