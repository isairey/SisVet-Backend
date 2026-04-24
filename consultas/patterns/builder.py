"""
Patrón Builder aplicado al módulo de Historias Clínicas.
Permite construir historias clínicas completas paso a paso.
Sara Sánchez - 2025
"""

from consultas.models import HistoriaClinica, Consulta, Prescripcion, Examen, HistorialVacuna


class HistoriaClinicaBuilder:
    """Construye una historia clínica paso a paso."""

    def __init__(self, mascota):
        self.mascota = mascota
        self.historia = None
        self.consulta_actual = None

    def crear_historia(self):
        self.historia = HistoriaClinica.objects.create(mascota=self.mascota)
        return self

    def agregar_consulta(self, veterinario, descripcion, diagnostico, notas=None):
        self.consulta_actual = Consulta.objects.create(
            mascota=self.mascota,
            veterinario=veterinario,
            descripcion_consulta=descripcion,
            diagnostico=diagnostico,
            notas_adicionales=notas or ""
        )
        return self

    def agregar_prescripcion(self, medicamento, cantidad, indicaciones=None):
        if not self.consulta_actual:
            raise ValueError("Debe agregar una consulta antes de prescribir medicamentos.")
        Prescripcion.objects.create(
            consulta=self.consulta_actual,
            medicamento=medicamento,
            cantidad=cantidad,
            indicaciones=indicaciones or ""
        )
        return self

    def agregar_vacuna(self, estado, descripcion=None):
        if not self.consulta_actual:
            raise ValueError("Debe agregar una consulta antes de registrar vacunas.")
        HistorialVacuna.objects.create(
            consulta=self.consulta_actual,
            estado=estado,
            vacunas_descripcion=descripcion or ""
        )
        return self

    def agregar_examen(self, tipo_examen, descripcion=None):
        if not self.consulta_actual:
            raise ValueError("Debe agregar una consulta antes de registrar exámenes.")
        Examen.objects.create(
            consulta=self.consulta_actual,
            tipo_examen=tipo_examen,
            descripcion=descripcion or ""
        )
        return self

    def obtener_historia(self):
        return self.historia