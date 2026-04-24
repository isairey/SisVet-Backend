from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from datetime import datetime
from django.conf import settings
from usuarios.serializers.auth import (
    ResetPasswordRequestSerializer,
    ResetPasswordConfirmSerializer,
)
from usuarios.models import ResetPasswordToken
from notificaciones.services import enviar_notificacion_generica

class ResetPasswordRequestView(generics.GenericAPIView):
    serializer_class = ResetPasswordRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(email=email)

        # Crear token
        token_obj = ResetPasswordToken.create_for_user(user, minutes=60)

        # Construir link apuntando al frontend real
        # Usa FRONTEND_URL de settings o default a localhost:5173 (Vite)
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        link = f"{frontend_url}/auth/reset-password?token={token_obj.token}"

        # Enviar notificación usando el servicio
        context = {
            'usuario_nombre': user.get_full_name(),
            'link': link,
            'anio_actual': datetime.now().year,
        }
        try:
            enviar_notificacion_generica('RESET_PASSWORD', context, user.email)
        except Exception:
            # No fallar si el envío falla; loguear en producción
            pass

        return Response({'message': 'Si el correo existe, se ha enviado un enlace para restablecer la contraseña.'}, status=status.HTTP_200_OK)


class ResetPasswordConfirmView(generics.GenericAPIView):
    serializer_class = ResetPasswordConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_obj = serializer.validated_data['token_obj']
        password = serializer.validated_data['password']

        user = token_obj.usuario
        user.set_password(password)
        user.save()

        token_obj.usado = True
        token_obj.save()

        # Enviar correo de confirmación de restablecimiento exitoso
        try:
            context = {
                'usuario_nombre': user.get_full_name(),
                'fecha_actual': datetime.now().strftime('%d/%m/%Y a las %H:%M'),
                'anio_actual': datetime.now().year,
            }
            enviar_notificacion_generica('PASSWORD_RESET_SUCCESS', context, user.email)
        except Exception as e:
            # No fallar si el envío falla; loguear en producción
            print(f"Error al enviar correo de confirmación de restablecimiento: {str(e)}")

        return Response({'message': 'Contraseña restablecida correctamente.'}, status=status.HTTP_200_OK)
