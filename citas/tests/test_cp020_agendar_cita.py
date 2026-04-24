from rest_framework import status
from django.urls import reverse
from .test_base import CitasAPITestCase
from citas.models import Cita
from citas.patterns.state import EstadoCita
from django.utils import timezone
from datetime import timedelta

class CP020AgendarCitaTest(CitasAPITestCase):
    
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.cliente_user)
        manana = timezone.now() + timedelta(days=1)
        self.fecha_futura = manana.replace(hour=10, minute=0, second=0, microsecond=0)

    def test_agendar_cita_exitosa(self):
        """CP-020: Cliente agenda cita correctamente (201 Created)"""
        url = reverse('cita-list')
        data = {
            "mascota_id": self.mascota.id,
            "veterinario_id": self.vet_user.id,
            "servicio_id": self.servicio.id,
            "fecha_hora": self.fecha_futura.isoformat()
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cita.objects.count(), 1)
        self.assertEqual(Cita.objects.first().estado, EstadoCita.AGENDADA)