from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .test_base import CitasAPITestCase

class FailFechaPasadaTest(CitasAPITestCase):

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.cliente_user)

    def test_agendar_horario_pasado(self):
        """Fallo: Intentar agendar en el pasado (400)"""
        ayer = timezone.now() - timedelta(days=1)
        url = reverse('cita-list')
        data = {
            "mascota_id": self.mascota.id,
            "veterinario_id": self.vet_user.id,
            "servicio_id": self.servicio.id,
            "fecha_hora": ayer.isoformat()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Buscamos una palabra clave en el error
        self.assertTrue("pasado" in str(response.data) or "past" in str(response.data))