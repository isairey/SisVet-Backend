"""
Tests para la creación de consultas veterinarias.
Incluye validaciones, creación anidada de prescripciones, exámenes y vacunas.
"""

from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime

from consultas.models import Consulta, Prescripcion, Examen, HistorialVacuna
from mascotas.models import Mascota, Especie, Raza
from usuarios.models import Cliente, Veterinario
from inventario.models import Producto, Categoria, Marca

User = get_user_model()


class CrearConsultaTestCase(APITestCase):
    """Tests para la creación de consultas"""

    def setUp(self):
        """Configuración inicial para todos los tests"""
        # Crear usuario veterinario
        self.user_veterinario = User.objects.create_user(
            username='vet_test',
            email='vet@test.com',
            password='testpass123',
            nombre='Dr. Juan',
            apellido='Pérez',
        )
        self.veterinario = Veterinario.objects.create(
            usuario=self.user_veterinario,
            especialidad='Medicina General',
            licencia='VET-001',
        )

        # Crear usuario cliente
        self.user_cliente = User.objects.create_user(
            username='cliente_test1',
            email='cliente@test.com',
            password='testpass123',
            nombre='María',
            apellido='González',
        )
        self.cliente = Cliente.objects.create(
            usuario=self.user_cliente,
            telefono='1234567890',
            direccion='Calle 123'
        )

        # Crear especie y raza
        self.especie = Especie.objects.create(nombre='Perro')
        self.raza = Raza.objects.create(
            nombre='Labrador',
            especie=self.especie
        )

        # Crear mascota
        self.mascota = Mascota.objects.create(
            nombre='Max',
            especie=self.especie,
            raza=self.raza,
            sexo='M',
            fecha_nacimiento='2020-01-15',
            peso=25.5,
            cliente=self.cliente
        )

        # Crear categoría y producto para prescripciones
        self.marca = Marca.objects.create(descripcion='PetCare')
        self.categoria = Categoria.objects.create(
            descripcion='Medicamentos'
        )
        self.medicamento = Producto.objects.create(
            descripcion='Amoxicilina',
            marca=self.marca,
            categoria=self.categoria,
            stock=100,
            stock_minimo=10,
            precio_venta=15.50,
            precio_compra=20.00,
        )

        # Cliente API
        self.client = APIClient()

    def test_crear_consulta_completa(self):
        """Prueba crear consulta con todos los componentes"""
        self.client.force_authenticate(user=self.user_veterinario)

        data = {
            'mascota': self.mascota.id,
            'veterinario': self.veterinario.usuario_id,
            'fecha_consulta': timezone.now().isoformat(),
            'descripcion_consulta': 'Consulta integral completa',
            'diagnostico': 'Infección respiratoria con necesidad de seguimiento',
            'notas_adicionales': 'Control en 15 días',
            'prescripciones': [
                {
                    'medicamento': self.medicamento.id,
                    'cantidad': 10,
                    'indicaciones': 'Cada 8 horas'
                }
            ],
            'examenes': [
                {
                    'tipo_examen': 'HEMOGRAMA',
                    'descripcion': 'Control'
                }
            ],
            'vacunas': {
                'estado': 'AL_DIA',
                'vacunas_descripcion': ''
            }
        }

        response = self.client.post('/api/v1/consultas/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Consulta.objects.count(), 1)
        self.assertEqual(Prescripcion.objects.count(), 1)
        self.assertEqual(Examen.objects.count(), 1)
        self.assertEqual(HistorialVacuna.objects.count(), 1)
        print("Test: Consulta completa creada exitosamente")

    def test_crear_consulta_sin_descripcion(self):
        """Prueba que falla al crear consulta sin descripción"""
        self.client.force_authenticate(user=self.user_veterinario)

        data = {
            'mascota': self.mascota.id,
            'veterinario': self.veterinario.usuario_id,
            'fecha_consulta': timezone.now().isoformat(),
            'descripcion_consulta': '',
            'diagnostico': 'Algún diagnóstico'
        }

        response = self.client.post('/api/v1/consultas/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('descripcion_consulta', response.data)
        print("Test: La consulta no se puede crear sin descripcion")

    def test_crear_consulta_sin_diagnostico(self):
        """Prueba que falla al crear consulta sin diagnóstico"""
        self.client.force_authenticate(user=self.user_veterinario)

        data = {
            'mascota': self.mascota.id,
            'veterinario': self.veterinario.usuario_id,
            'fecha_consulta': timezone.now().isoformat(),
            'descripcion_consulta': 'Alguna descripción',
            'diagnostico': ''
        }

        response = self.client.post('/api/v1/consultas/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('diagnostico', response.data)
        print("Test: La consulta no se puede crear sin diagnostico")

    def test_crear_consulta_vacunas_pendientes_sin_descripcion(self):
        """Prueba que falla al marcar vacunas pendientes sin especificar cuáles"""
        self.client.force_authenticate(user=self.user_veterinario)

        data = {
            'mascota': self.mascota.id,
            'veterinario': self.veterinario.usuario_id,
            'fecha_consulta': timezone.now().isoformat(),
            'descripcion_consulta': 'Consulta',
            'diagnostico': 'Diagnóstico',
            'vacunas': {
                'estado': 'PENDIENTE',
                'vacunas_descripcion': ''
            }
        }

        response = self.client.post('/api/v1/consultas/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("Test: La consulta no se puede crear si las vacunas estan pendientes y el campo esta vacio")
