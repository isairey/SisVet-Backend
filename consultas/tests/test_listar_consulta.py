"""
Tests para listar y filtrar consultas veterinarias.
Incluye paginación, búsqueda, filtros y ordenamiento.
"""
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from consultas.models import Consulta, HistorialVacuna
from mascotas.models import Mascota, Especie, Raza
from usuarios.models import Cliente, Veterinario

User = get_user_model()


class ListarConsultasTestCase(APITestCase):
    """Tests para listar consultas"""

    def setUp(self):
        """Configuración inicial"""
        # Crear veterinarios
        self.user_vet1 = User.objects.create_user(
            username='vet_test',
            email='vet1@test.com',
            password='testpass123',
            nombre='Dr. Juan',
            apellido='Pérez',
        )
        self.veterinario1 = Veterinario.objects.create(
            usuario=self.user_vet1,
            especialidad='Medicina General',
            licencia='VET-001',
        )

        self.user_vet2 = User.objects.create_user(
            username='vet_test2',
            email='vet2@test.com',
            password='testpass123',
            nombre='Dra. Ana',
            apellido='Martínez',
        )
        self.veterinario2 = Veterinario.objects.create(
            usuario=self.user_vet2,
            especialidad='Cirugía',
            licencia = 'VET-002',
        )

        # Crear clientes
        self.user_cliente1 = User.objects.create_user(
            username='cliente_test1',
            email='cliente1@test.com',
            password='testpass123',
            nombre='María',
            apellido='González',
        )
        self.cliente1 = Cliente.objects.create(
            usuario=self.user_cliente1,
            telefono='1234567890',
            direccion='Calle 123'
        )

        self.user_cliente2 = User.objects.create_user(
            username='cliente_test2',
            email='cliente2@test.com',
            password='testpass123',
            nombre='Pedro',
            apellido='López',
        )
        self.cliente2 = Cliente.objects.create(
            usuario=self.user_cliente2,
            telefono='0987654321',
            direccion='Avenida 456'
        )

        # Crear especies y razas
        self.especie_perro = Especie.objects.create(nombre='Perro')
        self.especie_gato = Especie.objects.create(nombre='Gato')
        self.raza_labrador = Raza.objects.create(nombre='Labrador', especie=self.especie_perro)
        self.raza_persa = Raza.objects.create(nombre='Persa', especie=self.especie_gato)

        # Crear mascotas
        self.mascota1 = Mascota.objects.create(
            nombre='Max',
            especie=self.especie_perro,
            raza=self.raza_labrador,
            sexo='M',
            fecha_nacimiento='2020-01-15',
            peso=25.5,
            cliente=self.cliente1
        )

        self.mascota2 = Mascota.objects.create(
            nombre='Luna',
            especie=self.especie_gato,
            raza=self.raza_persa,
            sexo='H',
            fecha_nacimiento='2021-03-10',
            peso=4.5,
            cliente=self.cliente1
        )

        self.mascota3 = Mascota.objects.create(
            nombre='Rocky',
            especie=self.especie_perro,
            raza=self.raza_labrador,
            sexo='M',
            fecha_nacimiento='2019-05-20',
            peso=30.0,
            cliente=self.cliente2
        )

        # Crear consultas variadas
        now = timezone.now()

        self.consulta1 = Consulta.objects.create(
            mascota=self.mascota1,
            veterinario=self.veterinario1,
            fecha_consulta=now - timedelta(days=5),
            descripcion_consulta='Control de rutina',
            diagnostico='Mascota en buen estado'
        )

        self.consulta2 = Consulta.objects.create(
            mascota=self.mascota1,
            veterinario=self.veterinario2,
            fecha_consulta=now - timedelta(days=2),
            descripcion_consulta='Infección respiratoria',
            diagnostico='Bronquitis leve'
        )

        self.consulta3 = Consulta.objects.create(
            mascota=self.mascota2,
            veterinario=self.veterinario1,
            fecha_consulta=now - timedelta(days=1),
            descripcion_consulta='Vacunación anual',
            diagnostico='Aplicación de vacunas'
        )

        self.consulta4 = Consulta.objects.create(
            mascota=self.mascota3,
            veterinario=self.veterinario2,
            fecha_consulta=now,
            descripcion_consulta='Dolor abdominal',
            diagnostico='Gastritis aguda'
        )

        self.client = APIClient()

    def test_listar_todas_consultas_veterinario(self):
        """Prueba que un veterinario puede ver todas las consultas"""
        self.client.force_authenticate(user=self.user_vet1)

        response = self.client.get('/api/v1/consultas/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        print("Test: Se muestran todas las consultas por veterinario")

    def test_listar_consultas_cliente_solo_sus_mascotas(self):
        """Prueba que un cliente solo ve consultas de sus mascotas"""
        self.client.force_authenticate(user=self.user_cliente1)

        response = self.client.get('/api/v1/consultas/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Cliente 1 tiene 2 mascotas con 3 consultas en total
        self.assertEqual(len(response.data['results']), 3)
        print("Test: Se muestran todas las consultas de sus mascotas a su cliente")

    def test_buscar_consultas_por_nombre_mascota(self):
        """Prueba buscar consultas por nombre de mascota"""
        self.client.force_authenticate(user=self.user_vet1)

        response = self.client.get('/api/v1/consultas/?search=Max')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        print("Test: Buscan todas las consultas segun el nombre de la mascota")

    def test_endpoint_consultas_por_mascota(self):
        """Prueba el endpoint personalizado para consultas por mascota"""
        self.client.force_authenticate(user=self.user_vet1)

        response = self.client.get(f'/api/v1/consultas/mascota/{self.mascota1.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        print("Test: Buscan todas las consultas segun el id de la mascota")

    def test_endpoint_consultas_por_veterinario(self):
        """Prueba el endpoint personalizado para consultas por veterinario"""
        self.client.force_authenticate(user=self.user_vet1)

        response = self.client.get(
            f'/api/v1/consultas/veterinario/{self.veterinario1.usuario_id}/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        print("Test: Lista todas las consultas segun el id del veteinario")

    def test_endpoint_estadisticas_consultas(self):
        """Prueba el endpoint de estadísticas"""
        self.client.force_authenticate(user=self.user_vet1)

        response = self.client.get('/api/v1/consultas/estadisticas/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_consultas', response.data)
        self.assertIn('consultas_por_mes', response.data)
        self.assertEqual(response.data['total_consultas'], 4)
        print("Test: Cuenta cuantas consultas se han realizado")

    def test_cliente_no_puede_ver_consultas_de_otro_cliente(self):
        """Prueba que un cliente no puede ver consultas de mascotas de otro cliente"""
        self.client.force_authenticate(user=self.user_cliente1)

        # Intentar acceder a consulta de mascota del cliente2
        response = self.client.get(f'/api/v1/consultas/mascota/{self.mascota3.id}/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        print("Test: El cliente solo puede ver las consultas de su mascota no de otras")