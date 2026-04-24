from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .test_base import CitasAPITestCase

class CP021DisponibilidadTest(CitasAPITestCase):

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.cliente_user)
        self.fecha_futura = timezone.now() + timedelta(days=1)

    def test_consultar_disponibilidad(self):
        """CP-021: Consultar horarios disponibles (200 OK)"""
        fecha_str = self.fecha_futura.date().isoformat()
        url = f"/api/v1/citas/disponibilidad/?veterinario_id={self.vet_user.id}&fecha={fecha_str}"
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('horarios_disponibles', response.data)
        # Asumimos que a las 8 AM está libre si no hay citas
        self.assertIn("08:00", response.data['horarios_disponibles'])