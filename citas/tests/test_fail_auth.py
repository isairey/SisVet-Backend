from rest_framework import status
from django.urls import reverse
from .test_base import CitasAPITestCase

class FailAuthTest(CitasAPITestCase):

    def test_agendar_sin_autenticacion(self):
        """Fallo: Intentar agendar sin login (401)"""
        
        self.client.force_authenticate(user=None)
        
        url = reverse('cita-list')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)