from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from usuarios.serializers.auth import CustomTokenObtainPairSerializer

# Jeronimo Rodriguez 10/31/2025 
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista personalizada para la obtención de tokens JWT (Login).

    - Endpoint: POST /api/v1/auth/login/
    - Permite autenticar al usuario y retornar:
        • access token
        • refresh token
        • información básica del usuario autenticado
    - Utiliza el serializer CustomTokenObtainPairSerializer.
    """
    serializer_class = CustomTokenObtainPairSerializer
