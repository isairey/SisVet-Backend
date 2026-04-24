from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

# Jeronimo Rodriguez 11/01/2025 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Endpoint para cerrar sesión.
    Añade el refresh token a la lista negra (si se implementa).
    """
    try:
        refresh_token = request.data.get('refresh')
        
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {'detail': 'Sesión cerrada exitosamente.'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'detail': 'Se requiere el refresh token.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as _:
        return Response(
            {'detail': 'Token inválido o ya expirado.'},
            status=status.HTTP_400_BAD_REQUEST
        )
