# consultas/views/consentimiento_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  # ¡Público!
from rest_framework import status
from django.utils import timezone
from consultas.models import Consulta


class ConfirmarConsentimientoView(APIView):
    """
    Endpoint público para que un cliente confirme un consentimiento
    haciendo clic en el enlace del correo.

    GET: Verifica el token y devuelve información de la consulta
    POST: Confirma el consentimiento con el token
    """
    permission_classes = [AllowAny]  # No requiere login

    def _obtener_consulta_por_token(self, token):
        """Helper para obtener la consulta por token."""
        if not token:
            return None
        try:
            return Consulta.objects.select_related(
                'mascota',
                'mascota__cliente',
                'mascota__cliente__usuario',
                'veterinario',
                'veterinario__usuario'
            ).get(consentimiento_token=token)
        except Consulta.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        """
        Verifica el token y devuelve información de la consulta.
        Útil para mostrar la página de confirmación antes de confirmar.
        """
        token = request.query_params.get('token')

        if not token:
            return Response(
                {
                    "error": "Token no proporcionado.",
                    "valid": False
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        consulta = self._obtener_consulta_por_token(token)

        if not consulta:
            return Response(
                {
                    "error": "Enlace de consentimiento inválido o expirado.",
                    "valid": False
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Preparar datos de respuesta
        datos = {
            "valid": True,
            "consulta_id": consulta.id,
            "mascota_nombre": consulta.mascota.nombre,
            "propietario_nombre": consulta.mascota.cliente.usuario.get_full_name(),
            "veterinario_nombre": consulta.veterinario.usuario.get_full_name() if consulta.veterinario and consulta.veterinario.usuario else "No asignado",
            "fecha_consulta": consulta.fecha_consulta.strftime("%d/%m/%Y %H:%M") if consulta.fecha_consulta else None,
            "diagnostico": consulta.diagnostico,
            "consentimiento_otorgado": consulta.consentimiento_otorgado,
            "consentimiento_fecha": consulta.consentimiento_fecha.strftime("%d/%m/%Y %H:%M") if consulta.consentimiento_fecha else None,
            "ya_confirmado": consulta.consentimiento_otorgado
        }

        return Response(datos, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Confirma el consentimiento con el token proporcionado.
        """
        token = request.data.get('token')

        if not token:
            return Response(
                {
                    "error": "Token no proporcionado.",
                    "success": False
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        consulta = self._obtener_consulta_por_token(token)

        if not consulta:
            return Response(
                {
                    "error": "Enlace de consentimiento inválido o expirado.",
                    "success": False
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar si ya está confirmado
        if consulta.consentimiento_otorgado:
            return Response(
                {
                    "success": True,
                    "message": "El consentimiento ya había sido confirmado anteriormente.",
                    "consulta_id": consulta.id,
                    "mascota_nombre": consulta.mascota.nombre,
                    "ya_confirmado": True
                },
                status=status.HTTP_200_OK
            )

        # Confirmar el consentimiento
        try:
            consulta.consentimiento_otorgado = True
            consulta.consentimiento_fecha = timezone.now()
            consulta.save(update_fields=['consentimiento_otorgado', 'consentimiento_fecha'])

            return Response(
                {
                    "success": True,
                    "message": "Consentimiento confirmado exitosamente.",
                    "consulta_id": consulta.id,
                    "mascota_nombre": consulta.mascota.nombre,
                    "consentimiento_fecha": consulta.consentimiento_fecha.strftime("%d/%m/%Y %H:%M"),
                    "ya_confirmado": False
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "error": f"Error al confirmar el consentimiento: {str(e)}",
                    "success": False
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )