from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from transacciones.services.factura_service import FacturaService
from transacciones.serializers.factura_serializer import FacturaSerializer
from transacciones.models.factura import Factura


class CrearFacturaDesdeCita(APIView):
    """
    Crea una factura desde una cita.
    Si ya existe una factura para esta cita, retorna información para reenvío de email.
    """
    def post(self, request, cita_id):
        try:
            factura = FacturaService.crear_factura_desde_cita(cita_id)
            serializer = FacturaSerializer(factura)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Si ya existe una factura, retornar información para reenvío
            factura_existente = Factura.objects.filter(cita_id=cita_id).exclude(estado='ANULADA').first()
            if factura_existente:
                return Response(
                    {
                        "error": str(e),
                        "factura_existente": FacturaSerializer(factura_existente).data,
                        "mensaje": "Use el endpoint de reenvío de email para enviar la factura nuevamente."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CrearFacturaDesdeConsulta(APIView):
    """
    Crea una factura desde una consulta.
    Si ya existe una factura para esta consulta, retorna información para reenvío de email.
    """
    def post(self, request, consulta_id):
        try:
            factura = FacturaService.crear_factura_desde_consulta(consulta_id)
            serializer = FacturaSerializer(factura)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Si ya existe una factura, retornar información para reenvío
            factura_existente = Factura.objects.filter(consulta_id=consulta_id).exclude(estado='ANULADA').first()
            if factura_existente:
                return Response(
                    {
                        "error": str(e),
                        "factura_existente": FacturaSerializer(factura_existente).data,
                        "mensaje": "Use el endpoint de reenvío de email para enviar la factura nuevamente."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )