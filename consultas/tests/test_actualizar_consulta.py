"""
Tests para la actualización de consultas veterinarias.
Incluye actualización de campos básicos y relaciones anidadas.
"""

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone

from consultas.models import Consulta, Prescripcion, Examen, HistorialVacuna
from mascotas.models import Mascota, Especie, Raza
from usuarios.models import Cliente, Veterinario
from inventario.models import Producto, Categoria, Marca

User = get_user_model()


class ActualizarConsultaTestCase(APITestCase):
    """Tests para la actualización de consultas"""

    def setUp(self):
        """Configuración inicial"""
        # Usuario veterinario
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
            licencia='VET-001'
        )

        # Usuario cliente
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

        # Especie, raza y mascota
        self.especie = Especie.objects.create(nombre='Perro')
        self.raza = Raza.objects.create(nombre='Labrador', especie=self.especie)
        self.mascota = Mascota.objects.create(
            nombre='Max',
            especie=self.especie,
            raza=self.raza,
            sexo='M',
            fecha_nacimiento='2020-01-15',
            peso=25.5,
            cliente=self.cliente
        )

        # Producto para prescripciones
        self.marca = Marca.objects.create(descripcion='PetCare')
        self.categoria = Categoria.objects.create(descripcion='Medicamentos')
        self.medicamento1 = Producto.objects.create(
            descripcion='Amoxicilina',
            marca=self.marca,
            categoria=self.categoria,
            stock=100,
            stock_minimo=10,
            precio_venta=15.50,
            precio_compra=20.00,
        )
        self.medicamento2 = Producto.objects.create(
            descripcion='Paracetamol',
            marca=self.marca,
            categoria=self.categoria,
            stock=50,
            stock_minimo=5,
            precio_venta=10.00,
            precio_compra=20.00,
        )

        # Consulta existente con prescripción y examen
        self.consulta = Consulta.objects.create(
            mascota=self.mascota,
            veterinario=self.veterinario,
            fecha_consulta=timezone.now(),
            descripcion_consulta='Consulta inicial',
            diagnostico='Diagnóstico inicial'
        )

        self.prescripcion = Prescripcion.objects.create(
            consulta=self.consulta,
            medicamento=self.medicamento1,
            cantidad=10,
            indicaciones='Cada 8 horas'
        )

        self.examen = Examen.objects.create(
            consulta=self.consulta,
            tipo_examen='HEMOGRAMA',
            descripcion='Hemograma inicial'
        )

        self.client = APIClient()

    def test_actualizar_descripcion_consulta(self):
        """Prueba actualizar solo la descripción de la consulta"""
        self.client.force_authenticate(user=self.user_veterinario)

        data = {
            'mascota': self.mascota.id,
            'veterinario': self.veterinario.usuario_id,
            'fecha_consulta': self.consulta.fecha_consulta.isoformat(),
            'descripcion_consulta': 'Consulta actualizada con nueva información',
            'diagnostico': self.consulta.diagnostico
        }

        response = self.client.put(
            f'/api/v1/consultas/{self.consulta.id}/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.consulta.refresh_from_db()
        self.assertEqual(
            self.consulta.descripcion_consulta,
            'Consulta actualizada con nueva información'
        )
        print("Test: La consulta fue actualizada exitosamente")

    def test_actualizar_diagnostico(self):
        """Prueba actualizar el diagnóstico"""
        self.client.force_authenticate(user=self.user_veterinario)

        data = {
            'mascota': self.mascota.id,
            'veterinario': self.veterinario.usuario_id,
            'fecha_consulta': self.consulta.fecha_consulta.isoformat(),
            'descripcion_consulta': self.consulta.descripcion_consulta,
            'diagnostico': 'Diagnóstico actualizado: Infección leve'
        }

        response = self.client.put(
            f'/api/v1/consultas/{self.consulta.id}/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.consulta.refresh_from_db()
        self.assertEqual(
            self.consulta.diagnostico,
            'Diagnóstico actualizado: Infección leve'
        )
        print("Test: El diagnostico fue actualizado exitosamente")

    def test_actualizar_prescripciones(self):
        """Prueba actualizar las prescripciones de una consulta"""
        self.client.force_authenticate(user=self.user_veterinario)

        # Contar prescripciones iniciales
        count_inicial = self.consulta.prescripciones.count()
        self.assertEqual(count_inicial, 1)

        data = {
            'mascota': self.mascota.id,
            'veterinario': self.veterinario.usuario_id,
            'fecha_consulta': self.consulta.fecha_consulta.isoformat(),
            'descripcion_consulta': self.consulta.descripcion_consulta,
            'diagnostico': self.consulta.diagnostico,
            'prescripciones': [
                {
                    'medicamento': self.medicamento2.id,
                    'cantidad': 5,
                    'indicaciones': 'Cada 12 horas si hay dolor'
                }
            ]
        }

        response = self.client.put(
            f'/api/v1/consultas/{self.consulta.id}/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que se reemplazó la prescripción
        self.consulta.refresh_from_db()
        self.assertEqual(self.consulta.prescripciones.count(), 1)

        nueva_prescripcion = self.consulta.prescripciones.first()
        self.assertEqual(nueva_prescripcion.medicamento, self.medicamento2)
        self.assertEqual(nueva_prescripcion.cantidad, 5)
        print("Test: Se actualizo la prescripcion correctamente")

    def test_agregar_examenes_a_consulta(self):
        """Prueba agregar exámenes adicionales a una consulta"""
        self.client.force_authenticate(user=self.user_veterinario)

        data = {
            'mascota': self.mascota.id,
            'veterinario': self.veterinario.usuario_id,
            'fecha_consulta': self.consulta.fecha_consulta.isoformat(),
            'descripcion_consulta': self.consulta.descripcion_consulta,
            'diagnostico': self.consulta.diagnostico,
            'examenes': [
                {
                    'tipo_examen': 'RAYOS_X',
                    'descripcion': 'Rayos X de tórax'
                },
                {
                    'tipo_examen': 'ECOGRAFIA',
                    'descripcion': 'Ecografía abdominal'
                }
            ]
        }

        response = self.client.put(
            f'/api/v1/consultas/{self.consulta.id}/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que se reemplazaron los exámenes
        self.consulta.refresh_from_db()
        self.assertEqual(self.consulta.examenes.count(), 2)
        print("Test: Se actualiza la examene correctamente")

    def test_actualizar_estado_vacunacion(self):
        """Prueba actualizar el estado de vacunación"""
        self.client.force_authenticate(user=self.user_veterinario)

        # Primero crear registro de vacunas
        HistorialVacuna.objects.create(
            consulta=self.consulta,
            estado='PENDIENTE',
            vacunas_descripcion='Rabia pendiente'
        )

        data = {
            'mascota': self.mascota.id,
            'veterinario': self.veterinario.usuario_id,
            'fecha_consulta': self.consulta.fecha_consulta.isoformat(),
            'descripcion_consulta': self.consulta.descripcion_consulta,
            'diagnostico': self.consulta.diagnostico,
            'vacunas': {
                'estado': 'AL_DIA',
                'vacunas_descripcion': ''
            }
        }

        response = self.client.put(
            f'/api/v1/consultas/{self.consulta.id}/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar nuevo estado
        self.consulta.refresh_from_db()
        vacuna = self.consulta.vacunas.first()
        self.assertEqual(vacuna.estado, 'AL_DIA')
        print("Test: Se actualiza la vacuna correctamente")

    def test_actualizar_consulta_sin_descripcion_falla(self):
        """Prueba que falla al intentar actualizar sin descripción"""
        self.client.force_authenticate(user=self.user_veterinario)

        data = {
            'mascota': self.mascota.id,
            'veterinario': self.veterinario.usuario_id,
            'fecha_consulta': self.consulta.fecha_consulta.isoformat(),
            'descripcion_consulta': '',
            'diagnostico': self.consulta.diagnostico
        }

        response = self.client.put(
            f'/api/v1/consultas/{self.consulta.id}/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("Test: La consulta no se puede actualizar sin el campo descripcion")

    def test_actualizar_consulta_sin_diagnostico_falla(self):
        """Prueba que falla al intentar actualizar sin diagnóstico"""
        self.client.force_authenticate(user=self.user_veterinario)

        data = {
            'mascota': self.mascota.id,
            'veterinario': self.veterinario.usuario_id,
            'fecha_consulta': self.consulta.fecha_consulta.isoformat(),
            'descripcion_consulta': self.consulta.descripcion_consulta,
            'diagnostico': ''
        }

        response = self.client.put(
            f'/api/v1/consultas/{self.consulta.id}/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("Test: La consulta no se puede actualizar sin el campo diagnostico")
