from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from usuarios.serializers.auth import UsuarioPerfilSerializer

class PerfilView(generics.RetrieveUpdateAPIView):
    """
    API endpoint que permite a un usuario autenticado visualizar y actualizar su perfil.

    Esta vista hereda de `RetrieveUpdateAPIView`, lo que proporciona automáticamente:
    - **GET**: para recuperar los datos del usuario autenticado.
    - **PUT/PATCH**: para actualizar los datos personales o del perfil asociado.

    El serializer utilizado (`UsuarioPerfilSerializer`) se encarga de representar
    la información completa del usuario, incluyendo:
        - Datos básicos (nombre, email, estado).
        - Roles asignados.
        - Perfiles extendidos (veterinario, practicante o cliente).
    
    Requiere autenticación mediante JWT.
    """
    
    serializer_class = UsuarioPerfilSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Retorna el usuario autenticado."""
        return self.request.user
