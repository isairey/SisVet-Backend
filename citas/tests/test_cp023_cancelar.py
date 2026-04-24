from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .test_base import CitasAPITestCase
from citas.models import Cita
from citas.patterns.state import EstadoCita

class CP023CancelarTest(CitasAPITestCase):

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.cliente_user)
        self.fecha_futura = timezone.now() + timedelta(days=1)
        
        # Creamos la cita para luego cancelarla
        self.cita = Cita.objects.create(
            mascota=self.mascota, veterinario=self.vet_user, 
            servicio=self.servicio, fecha_hora=self.fecha_futura,
            estado=EstadoCita.AGENDADA
        )

    def test_cancelar_cita_exitosa(self):
        """CP-023: Cancelar una cita (200 OK)"""
        url = reverse('cita-cancelar', kwargs={'pk': self.cita.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cita.refresh_from_db()
        self.assertEqual(self.cita.estado, EstadoCita.CANCELADA)