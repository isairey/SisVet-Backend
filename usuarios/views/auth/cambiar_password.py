from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from usuarios.serializers.crud import CambiarPasswordSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cambiar_password_view(request):
    """
    Endpoint para que el usuario autenticado cambie su contraseña.
    """
    serializer = CambiarPasswordSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        # Cambiar la contraseña
        user = request.user
        user.set_password(serializer.validated_data['password_nueva'])
        user.save()
        
        return Response(
            {'detail': 'Contraseña actualizada correctamente.'},
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
