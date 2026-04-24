from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from usuarios.models import Usuario, Rol, UsuarioRol
from citas.models import Servicio

class ServiciosCRUDTest(APITestCase):

    def setUp(self):
        # 1. Crear Admin (Solo admin/recepcionista deberían gestionar servicios)
        self.rol_admin = Rol.objects.create(nombre='administrador')
        self.admin_user = Usuario.objects.create_user(
            username='admin_test', password='password123', email='admin@test.com',
            nombre='Admin', apellido='Test'
        )
        UsuarioRol.objects.create(usuario=self.admin_user, rol=self.rol_admin)
        
        # 2. Autenticar
        self.client.force_authenticate(user=self.admin_user)

        # 3. Crear un servicio base para las pruebas
        self.servicio = Servicio.objects.create(nombre='Vacunación', costo=30000)

    def test_crear_servicio_exitoso(self):
        """Prueba crear un nuevo servicio (POST)"""
        url = reverse('servicio-list') # /api/v1/servicios/
        data = {"nombre": "Ecografía", "costo": 80000}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Servicio.objects.count(), 2) # El base + el nuevo

    def test_actualizar_servicio_exitoso(self):
        """Prueba actualizar precio de servicio (PATCH)"""
        url = reverse('servicio-detail', kwargs={'pk': self.servicio.id})
        data = {"costo": 35000}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.servicio.refresh_from_db()
        self.assertEqual(self.servicio.costo, 35000)

    def test_eliminar_servicio_exitoso(self):
        """Prueba eliminar un servicio (DELETE)"""
        url = reverse('servicio-detail', kwargs={'pk': self.servicio.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Servicio.objects.filter(id=self.servicio.id).exists())