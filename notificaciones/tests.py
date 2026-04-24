# notificaciones/tests.py
from django.test import TestCase
from unittest.mock import patch 
from citas.models import Cita, Servicio
from usuarios.models import Usuario, Rol, Cliente, UsuarioRol
from mascotas.models import Mascota, Especie, Raza
from django.utils import timezone
import datetime

# Importamos el *manejador* que queremos probar
from .handlers.handler_cita import handle_cita_agendada

class NotificacionesHandlersTests(TestCase):

    def setUp(self):
        # 1. Crear Roles
        self.rol_cliente = Rol.objects.create(nombre='cliente')
        self.rol_vet = Rol.objects.create(nombre='veterinario')

        # 2. Crear Usuarios y Perfil Cliente
        self.cliente_user = Usuario.objects.create_user(
            username='cliente_test_email', 
            password='password123',
            email='cliente@test.com',
            nombre='Cliente'
        )
        UsuarioRol.objects.create(usuario=self.cliente_user, rol=self.rol_cliente)
        self.perfil_cliente = Cliente.objects.create(usuario=self.cliente_user, telefono="123")

        self.vet_user = Usuario.objects.create_user(
            username='vet_test_email', 
            email='veterinario@test.com',
            password='password123', 
            nombre="Dr.", 
            apellido="Test"
        )
        UsuarioRol.objects.create(usuario=self.vet_user, rol=self.rol_vet)

        # 3. Crear Especie/Raza
        self.especie = Especie.objects.create(nombre="Perro")
        self.raza = Raza.objects.create(nombre="Labrador", especie=self.especie)

        # 4. Crear Mascota y Servicio
        self.mascota = Mascota.objects.create(
            nombre='Fido', 
            cliente=self.perfil_cliente,
            especie=self.especie,
            raza=self.raza,
            sexo='M'
        )
        self.servicio = Servicio.objects.create(nombre='Servicio Email Test', costo=100)

        # 5. Crear Cita
        self.cita = Cita.objects.create(
            mascota=self.mascota,
            veterinario=self.vet_user,
            servicio=self.servicio,
            fecha_hora=timezone.now() + datetime.timedelta(days=2)
        )

    # --- NUEVA PRUEBA ---
    # Interceptamos el servicio que realmente envía el correo
    @patch('notificaciones.handlers.handler_cita.enviar_notificacion_generica')
    def test_handler_de_cita_agendada_llama_al_servicio(self, mock_enviar_notificacion):
        
        """
        Prueba que 'handler_cita.py' recibe la señal 
        y llama al servicio de notificaciones.
        """
        
        # 1. Llamamos al handler manualmente, simulando una señal
        handle_cita_agendada(sender=Cita, cita=self.cita)

        # 2. Verificamos que el "espía" (mock_enviar_notificacion) fue llamado 1 vez
        self.assertEqual(mock_enviar_notificacion.call_count, 1)

        # 3. Verificamos los argumentos (qué se le pasó al espía)
        args, kwargs = mock_enviar_notificacion.call_args
        
        self.assertEqual(kwargs['evento'], 'CITA_CREADA')
        self.assertEqual(kwargs['to_email'], 'cliente@test.com')
        self.assertEqual(kwargs['context']['propietario_nombre'], 'Cliente')
        self.assertEqual(kwargs['context']['mascota_nombre'], 'Fido')