"""
Profile serializers package - Serializers para modelos de perfiles extendidos.
"""
from .rol_serializer import RolSerializer
from .veterinario_serializer import VeterinarioSerializer
from .practicante_serializer import PracticanteSerializer
from .cliente_serializer import ClienteSerializer

__all__ = [
    'RolSerializer',
    'VeterinarioSerializer',
    'PracticanteSerializer',
    'ClienteSerializer',
]
