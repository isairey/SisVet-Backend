"""
Tests para la eliminación de consultas veterinarias.
Verifica que las consultas y sus relaciones se eliminan correctamente.
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


class EliminarConsultaTestCase(APITestCase):
    """Tests para la eliminación de consultas"""

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
            licencia = 'VET-001',
        )

        # Usuario administrador
        self.user_admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            nombre='Admin',
            apellido='Sistema',
            is_staff=True,
            is_superuser=True
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

        # Mascota
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

        # Producto
        self.marca = Marca.objects.create(descripcion='PetCare')
        self.categoria = Categoria.objects.create(descripcion='Medicamentos')
        self.medicamento = Producto.objects.create(
            descripcion='Amoxicilina',
            marca=self.marca,
            categoria=self.categoria,
            stock=100,
            stock_minimo=10,
            precio_venta=15.50,
            precio_compra=20.00,
        )

        # Crear consulta con relaciones
        self.consulta = Consulta.objects.create(
            mascota=self.mascota,
            veterinario=self.veterinario,
            fecha_consulta=timezone.now(),
            descripcion_consulta='Consulta de prueba',
            diagnostico='Diagnóstico de prueba'
        )

        # Prescripción
        self.prescripcion = Prescripcion.objects.create(
            consulta=self.consulta,
            medicamento=self.medicamento,
            cantidad=10,
            indicaciones='Cada 8 horas'
        )

        # Examen
        self.examen = Examen.objects.create(
            consulta=self.consulta,
            tipo_examen='HEMOGRAMA',
            descripcion='Hemograma completo'
        )

        # Historial de vacunas
        self.vacuna = HistorialVacuna.objects.create(
            consulta=self.consulta,
            estado='AL_DIA',
            vacunas_descripcion=''
        )

        self.client = APIClient()

    def test_eliminar_consulta_exitoso(self):
        """Prueba eliminar una consulta exitosamente"""
        self.client.force_authenticate(user=self.user_veterinario)

        # Verificar que existe
        self.assertTrue(Consulta.objects.filter(id=self.consulta.id).exists())

        response = self.client.delete(f'/api/v1/consultas/{self.consulta.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verificar que se eliminó
        self.assertFalse(Consulta.objects.filter(id=self.consulta.id).exists())
        print("Test: La consulta se elimino exitosamente")

    def test_cliente_no_puede_eliminar_consulta(self):
        """Prueba que un cliente no puede eliminar consultas"""
        self.client.force_authenticate(user=self.user_cliente)

        response = self.client.delete(f'/api/v1/consultas/{self.consulta.id}/')

        # Debería ser 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verificar que la consulta sigue existiendo
        self.assertTrue(Consulta.objects.filter(id=self.consulta.id).exists())
        print("Test: La consulta mo se puede eliminar ya que eres cliente")
