# notificaciones/handlers/_helpers.py

from citas.models import Cita
from consultas.models import Consulta # Importamos el modelo de Consulta
from usuarios.models import Usuario, Cliente
from django.conf import settings
from datetime import datetime
from zoneinfo import ZoneInfo

FRONTEND_URL = getattr(settings, "FRONTEND_URL", "http://localhost:3000")

"""
Responsabilidad Única: Convertir instancias de modelo (Cita, Consulta)
en el "contexto" genérico que nuestros servicios de notificación esperan.
"""

def preparar_contexto_cita(cita: Cita) -> dict:
    """Extrae datos de una Cita para el contexto de notificación."""
    try:
        # Hacemos la consulta optimizada aquí
        cita_con_datos = Cita.objects.select_related(
            'mascota__cliente__usuario', 'veterinario', 'servicio'
        ).get(id=cita.id)
        
        usuario_cliente = cita_con_datos.mascota.cliente.usuario

        # Convertir fecha_hora de UTC a hora local de Colombia antes de formatear
        fecha_hora_colombia = cita_con_datos.fecha_hora.astimezone(ZoneInfo('America/Bogota'))
        
        context = {
            # Datos del destinatario
            'propietario_nombre': usuario_cliente.nombre,
            'to_email': usuario_cliente.email,
            
            # Datos específicos del evento
            'mascota_nombre': cita_con_datos.mascota.nombre,
            'fecha_hora': fecha_hora_colombia.strftime('%d-%b-%Y %I:%M %p'),
            'veterinario_nombre': cita_con_datos.veterinario.get_full_name(),
            'servicio_nombre': cita_con_datos.servicio.nombre,
            'anio_actual': datetime.now().year
        }
        return context
    except Exception as e:
        print(f"Error al preparar contexto de Cita {cita.id}: {e}")
        return None


def preparar_contexto_consulta(consulta: Consulta) -> dict:
    """Extrae datos de una Consulta para el contexto de notificación."""
    try:
        consulta_con_datos = Consulta.objects.select_related(
            'mascota__cliente__usuario', 'veterinario__usuario'  # Asegúrate de llegar al usuario del vet
        ).get(id=consulta.id)

        usuario_cliente = consulta_con_datos.mascota.cliente.usuario

        # --- Lógica del Link de Confirmación ---
        token = consulta_con_datos.consentimiento_token
        # Esta es la URL que el cliente final (frontend) recibirá
        confirmation_url = f"{FRONTEND_URL}/confirmar-consentimiento/?token={token}"

        context = {
            # Datos del destinatario
            'propietario_nombre': usuario_cliente.nombre,
            'to_email': usuario_cliente.email,

            # Datos específicos del evento
            'mascota_nombre': consulta_con_datos.mascota.nombre,
            'veterinario_nombre': consulta_con_datos.veterinario.usuario.get_full_name(),
            'diagnostico': consulta_con_datos.diagnostico,

            # La URL de confirmación para el botón
            'confirmation_url': confirmation_url,
            'anio_actual': datetime.now().year
        }
        return context
    except Exception as e:
        print(f"Error al preparar contexto de Consulta {consulta.id}: {e}")
        return None