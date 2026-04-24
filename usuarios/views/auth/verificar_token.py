from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verificar_token_view(request):
    """
    Endpoint para verificar si el token es válido.
    Útil para el frontend para validar sesiones.
    """
    return Response({
        'valid': True,
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'nombre_completo': request.user.get_full_name(),
            'roles': [ur.rol.nombre for ur in request.user.usuario_roles.select_related('rol')],
        }
    }, status=status.HTTP_200_OK)
