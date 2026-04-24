from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .test_base import CitasAPITestCase
from citas.models import Cita

class FailHorarioOcupadoTest(CitasAPITestCase):

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.cliente_user)
        self.fecha_futura = timezone.now() + timedelta(days=1)
        
        # 1. Ocupamos el horario creando una cita previa
        Cita.objects.create(
            mascota=self.mascota, veterinario=self.vet_user, 
            servicio=self.servicio, fecha_hora=self.fecha_futura
        )

    def test_agendar_horario_ocupado(self):
        """Fallo: Intentar agendar cuando el veterinario ya tiene cita (400)"""
        url = reverse('cita-list')
        data = {
            "mascota_id": self.mascota.id,
            "veterinario_id": self.vet_user.id,
            "servicio_id": self.servicio.id,
            "fecha_hora": self.fecha_futura.isoformat() # Misma fecha/hora
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("no está disponible", str(response.data))