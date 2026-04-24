"""
Profiles models package - Modelos de perfiles extendidos para usuarios.
"""
from .veterinario import Veterinario
from .practicante import Practicante
from .cliente import Cliente

__all__ = [
    'Veterinario',
    'Practicante',
    'Cliente',
]
