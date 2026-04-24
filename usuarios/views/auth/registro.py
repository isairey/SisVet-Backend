from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from usuarios.serializers.auth import RegistroSerializer

# Jeronimo Rodriguez 10/30/2025 
class RegistroView(generics.CreateAPIView):
    """
    Vista de API para el auto-registro de nuevos clientes en el sistema.

    Esta vista permite que cualquier usuario (sin autenticación previa)
    se registre como cliente, generando automáticamente su rol correspondiente
    y devolviendo un par de tokens JWT (refresh y access) para autenticación inmediata.
    """
    serializer_class = RegistroSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args,     **kwargs):
        """
        Procesa la solicitud de registro:
        1. Valida los datos ingresados mediante el serializer.
        2. Crea el usuario con rol 'cliente' y su perfil asociado.
        3. Genera tokens JWT para el nuevo usuario.
        4. Retorna la información básica del usuario y los tokens de autenticación.
        """

        # Validar los datos enviados
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Crear el nuevo usuario
        user = serializer.save()
        
        # Generar tokens JWT para el nuevo usuario
        refresh = RefreshToken.for_user(user)
        
        # Respuesta exitosa con la información del usuario y los tokens
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'nombre_completo': user.get_full_name(),
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Usuario registrado exitosamente.'
        }, status=status.HTTP_201_CREATED)
