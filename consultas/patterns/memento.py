"""
Patrón Memento aplicado al módulo de Historias Clínicas.
Permite guardar y restaurar estados previos de la historia clínica.
Sara Sánchez
03 noviembre 2025
"""

import json
from datetime import datetime


class HistoriaClinicaMemento:
    """Almacena el estado de la historia clínica en un momento determinado."""

    def __init__(self, estado):
        self.estado = estado
        self.fecha_guardado = datetime.now()

    def obtener_estado(self):
        return self.estado


class GestorMementos:
    """Administra los snapshots (versiones) de historias clínicas."""

    def __init__(self):
        self._historial = []

    def guardar(self, historia_clinica):
        """Guarda el estado actual de una historia clínica."""
        estado = {
            "mascota": historia_clinica.mascota.nombre,
            "estado_vacunacion_actual": historia_clinica.estado_vacunacion_actual,
            "fecha_actualizacion": str(historia_clinica.fecha_actualizacion),
        }
        self._historial.append(HistoriaClinicaMemento(json.dumps(estado)))

    def restaurar(self, historia_clinica, indice):
        """Restaura un estado anterior."""
        memento = self._historial[indice]
        estado = json.loads(memento.obtener_estado())
        historia_clinica.estado_vacunacion_actual = estado["estado_vacunacion_actual"]
        historia_clinica.save(update_fields=['estado_vacunacion_actual'])
        return historia_clinica

    def listar_versiones(self):
        """Devuelve la lista de versiones guardadas."""
        return [m.fecha_guardado.strftime("%d/%m/%Y %H:%M") for m in self._historial]