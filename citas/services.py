from datetime import datetime, time, timedelta
from django.utils import timezone
from .models import Cita, Servicio
from usuarios.models import Usuario
from mascotas.models import Mascota
from rest_framework.exceptions import ValidationError, PermissionDenied

def obtener_horarios_disponibles(veterinario_id: str, fecha: datetime.date) -> list:
    """
    Calcula los horarios disponibles para un veterinario en una fecha específica.
    Implementa el Patrón Composite (horario_base - citas_programadas).
    """

    # 1. Definir el horario base (Composite Principal)

    horario_base_dia = []
    hora_inicio = time(8, 0)
    hora_fin = time(17, 0) # 5 PM
    intervalo = timedelta(minutes=30)

    hora_actual = datetime.combine(fecha, hora_inicio)
    hora_fin_dt = datetime.combine(fecha, hora_fin)

    while hora_actual < hora_fin_dt:
        # Solo agregar si la hora es futura (respecto al momento actual)
        if fecha == timezone.now().date():
            # Si es hoy, solo mostrar horas que no hayan pasado
            if hora_actual.time() > timezone.now().time():
                horario_base_dia.append(hora_actual.time())
        elif fecha > timezone.now().date(): # Si es un día futuro, agregar todos
             horario_base_dia.append(hora_actual.time())
        hora_actual += intervalo

    # 2. Obtener los horarios ocupados (Composite a restar)
    citas_programadas = Cita.objects.filter(
        veterinario_id=veterinario_id,
        fecha_hora__date=fecha,
        estado=Cita.ESTADO_AGENDADA # Solo contar las agendadas
    ).values_list('fecha_hora', flat=True)

    # Convertir datetimes (que tienen zona horaria) a solo time para comparar
    horarios_ocupados = {cita_dt.astimezone(timezone.get_current_timezone()).time() for cita_dt in citas_programadas}

    # 3. Restar (Queso - Huecos)
    horarios_libres = [hora for hora in horario_base_dia if hora not in horarios_ocupados]

    # 4. Formatear para el futuro frontend
    return [hora.strftime("%H:%M") for hora in horarios_libres]


#Agendar cita:

def agendar_nueva_cita(data: dict, usuario: Usuario) -> Cita:
    """
    Servicio (Patrón Command) para crear una nueva cita (RF-004).
    Creamos una función agendar_nueva_cita. Esta función es un "Comando".
    Encapsula (envuelve) toda la lógica necesaria para realizar la acción de "agendar"
    """

    mascota_id = data.get('mascota_id')
    veterinario_id = data.get('veterinario_id')
    fecha_hora_str = data.get('fecha_hora')

    # --- 1. Validación de Lógica de Negocio ---
    try:
        mascota = Mascota.objects.get(id=mascota_id)
        veterinario = Usuario.objects.get(id=veterinario_id)
    except (Mascota.DoesNotExist, Usuario.DoesNotExist):
        raise ValidationError("La mascota o el veterinario no existen.")

    # Verificación de permisos: El cliente solo puede agendar para sus mascotas
    if 'cliente' in [r.nombre for r in usuario.usuario_roles.all()]:
        if mascota.propietario != usuario:
            raise PermissionDenied("No tienes permiso para agendar citas para esta mascota.")

    # Validación de Disponibilidad (RF-005, CP-021)
    # 'rstrip' quita la 'Z' de la hora (UTC) para que Python la entienda
    fecha_hora = timezone.make_aware(datetime.fromisoformat(fecha_hora_str.rstrip("Z")))

    horarios_libres_str = [h for h in obtener_horarios_disponibles(veterinario.id, fecha_hora.date())]

    if fecha_hora.strftime("%H:%M") not in horarios_libres_str:
        raise ValidationError("Conflicto de Horario: El veterinario no está disponible a esta hora.")

    # --- 2. Ejecución (Creación) ---
    cita = Cita.objects.create(
        mascota=mascota,
        veterinario=veterinario,
        servicio_id=data.get('servicio_id'),
        fecha_hora=fecha_hora,
        # 'observaciones' es el nombre que usé en tu modelo, cámbialo si usaste 'notas'
        observaciones=data.get('observaciones', ''),
        estado=Cita.ESTADO_AGENDADA # <-- Patrón State: estado inicial
    )

    # --- 3. Post-Acción (Patrón Observer) ---
    # Notificamos a los "observadores" (ej. servicio de email) que se creó una cita.
    notificar_observadores(evento="CITA_CREADA", cita=cita) # (RF-008)

    return cita

# cancelar y reagendar

def cancelar_cita(cita_id: str, usuario: Usuario) -> Cita:
    """
    Servicio (Patrón Command) para cancelar una cita (RF-007).
    Implementa Patrón State (Agendada -> Cancelada).
    Implementa Patrón Observer (Notifica cancelación).
    """
    try:
        cita = Cita.objects.get(id=cita_id)
    except Cita.DoesNotExist:
        raise ValidationError("La cita no existe.")

    # Verificación de permisos (RF-007)
    es_propietario = cita.mascota.propietario == usuario
    es_recepcionista = 'recepcionista' in [r.nombre for r in usuario.usuario_roles.all()]

    if not es_propietario and not es_recepcionista:
         raise PermissionDenied("No tienes permiso para cancelar esta cita.")

    # --- Lógica del Patrón State ---
    if cita.estado == Cita.ESTADO_CANCELADA:
        raise ValidationError("Esta cita ya ha sido cancelada.")

    cita.estado = Cita.ESTADO_CANCELADA # Cambio de estado
    cita.save()

    # --- Lógica del Patrón Observer --- (RF-008)
    notificar_observadores(evento="CITA_CANCELADA", cita=cita)

    return cita

def reagendar_cita(cita_id: str, nueva_fecha_hora_str: str, usuario: Usuario) -> Cita:
    """
    Servicio (Patrón Command) para reagendar una cita. (RF-006).
    """
    try:
        cita = Cita.objects.get(id=cita_id)
    except Cita.DoesNotExist:
        raise ValidationError("La cita no existe.")

    # (Aquí iría la lógica de permisos, similar a cancelar_cita)
    es_propietario = cita.mascota.propietario == usuario
    es_recepcionista = 'recepcionista' in [r.nombre for r in usuario.usuario_roles.all()]
    if not es_propietario and not es_recepcionista:
         raise PermissionDenied("No tienes permiso para reagendar esta cita.")

    # --- Lógica de Negocio ---
    # 1. Validar la nueva hora
    nueva_fecha_hora = timezone.make_aware(datetime.fromisoformat(nueva_fecha_hora_str.rstrip("Z")))
    horarios_libres_str = [h for h in obtener_horarios_disponibles(cita.veterinario.id, nueva_fecha_hora.date())]

    if nueva_fecha_hora.strftime("%H:%M") not in horarios_libres_str:
        # Re-validar por si es la misma hora (solo cambió el día)
         if Cita.objects.filter(veterinario=cita.veterinario, fecha_hora=nueva_fecha_hora, estado=Cita.ESTADO_AGENDADA).exists():
            raise ValidationError("Conflicto de Horario: El veterinario no está disponible a esta hora.")

    # 2. Actualizar (Patrón State)
    cita.fecha_hora = nueva_fecha_hora
    cita.estado = Cita.ESTADO_AGENDADA # Vuelve a "Agendada"
    cita.save()

    # --- Lógica del Patrón Observer --- (RF-008)
    notificar_observadores(evento="CITA_REAGENDADA", cita=cita)

    return cita

# --- LÓGICA DE NOTIFICACIÓN (Patrón Observer) ---
def notificar_observadores(evento: str, cita: Cita):
    """
    Simula un notificador (Patrón Observer).
    En un proyecto real, esto llamaría a un servicio de Celery/Redis
    para enviar emails (RF-008).
    """
    print(f"--- 📣 NOTIFICACIÓN ({evento}) ---")
    print(f"   Cita: {cita.id}")
    print(f"   Mascota: {cita.mascota.nombre}")
    print(f"   Fecha: {cita.fecha_hora}")
    print(f"   Estado: {cita.estado}")
    print("---------------------------------")