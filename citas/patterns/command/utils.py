from datetime import datetime
from django.utils import timezone
from rest_framework.exceptions import ValidationError

def parsear_fecha_hora(fecha_input):
    """
    Parsea un input de fecha (str o datetime) a un datetime con zona horaria.
    """
    if isinstance(fecha_input, str):
        # Elimina la Z si viene en formato ISO UTC string
        fecha_str = fecha_input.rstrip("Z")
        try:
            fecha = datetime.fromisoformat(fecha_str)
        except ValueError:
            raise ValidationError("Formato de fecha inválido.")
        
        if timezone.is_naive(fecha):
            return timezone.make_aware(fecha)
        return fecha

    elif isinstance(fecha_input, datetime):
        if timezone.is_naive(fecha_input):
            return timezone.make_aware(fecha_input)
        return fecha_input

    raise ValidationError("El campo 'fecha_hora' tiene un tipo no válido.")