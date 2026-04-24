"""
Patrón Composite aplicado al módulo de Historias Clínicas.
Permite tratar una historia clínica como una estructura jerárquica de componentes.
Sara Sánchez
03 noviembre 2025
"""

from abc import ABC, abstractmethod


# --- COMPONENTE BASE ---
class ComponenteHistoria(ABC):
    """Interfaz común para todos los componentes (hojas y compuestos)."""

    @abstractmethod
    def mostrar(self):
        pass


# --- COMPONENTE HOJA ---
class ConsultaHoja(ComponenteHistoria):
    """Representa una consulta individual (nodo hoja)."""

    def __init__(self, consulta):
        self.consulta = consulta

    def mostrar(self):
        return (
            f"Consulta del {self.consulta.fecha_consulta.strftime('%d/%m/%Y')} "
            f"- {self.consulta.mascota.nombre}: {self.consulta.descripcion_consulta[:50]}"
        )

# --- COMPONENTE COMPUESTO ---
class HistoriaClinicaCompuesta(ComponenteHistoria):
    """Representa una historia clínica completa con múltiples componentes."""

    def __init__(self, historia_clinica):
        self.historia_clinica = historia_clinica
        self.componentes = []

    def agregar(self, componente: ComponenteHistoria):
        self.componentes.append(componente)

    def eliminar(self, componente: ComponenteHistoria):
        self.componentes.remove(componente)

    def mostrar(self):
        resultado = [f"Historia Clínica de {self.historia_clinica.mascota.nombre}:"]
        for componente in self.componentes:
            resultado.append(f"  - {componente.mostrar()}")
        return "\n".join(resultado)