"""
Re-export fixtures comunes del paquete `usuarios.tests.conftest`.

Se coloca este `conftest.py` local para que los tests en
`mascotas/tests/` puedan aprovechar las mismas fixtures (api_client,
usuario_cliente, etc.) definidas en `usuarios/tests/conftest.py`.
"""
from usuarios.tests.conftest import *  # noqa: F403, F401
