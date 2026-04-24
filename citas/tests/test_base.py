from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta

# Importaciones de modelos de otras apps
from usuarios.models import Usuario, Rol, Cliente, UsuarioRol, Veterinario
from mascotas.models import Mascota, Especie, Raza
from citas.models import Servicio, Cita
from citas.patterns.state import EstadoCita 

class CitasAPITestCase(APITestCase):
    """
    Clase base para todas las pruebas de Citas.
    Crea un entorno de prueba con usuarios y mascotas.
    """
    
    def setUp(self):
        """Configuración que se ejecuta ANTES de cada prueba."""
        
        # 1. Crear Roles
        self.rol_cliente = Rol.objects.create(nombre='cliente')
        self.rol_veterinario = Rol.objects.create(nombre='veterinario')

        # 2. Crear Usuario Cliente
        self.cliente_user = Usuario.objects.create_user(
            username='cliente_prueba', 
            password='password123',
            email='cliente@test.com',
            nombre='Cliente',
            apellido='Prueba'
        )
        UsuarioRol.objects.create(usuario=self.cliente_user, rol=self.rol_cliente)
        # Usamos el perfil 'perfil_cliente' que define el modelo Usuario
        self.perfil_cliente = Cliente.objects.create(usuario=self.cliente_user, telefono="12345") 

        # 3. Crear Usuario Veterinario
        self.vet_user = Usuario.objects.create_user(
            username='vet_prueba', 
            password='password123',
            email='vet@test.com',
            nombre='Dr. Vet',
            apellido='Prueba'
        )
        UsuarioRol.objects.create(usuario=self.vet_user, rol=self.rol_veterinario)
        # Usamos el perfil 'perfil_veterinario'
        Veterinario.objects.create(usuario=self.vet_user, licencia="12345-TEST") 

        # 4. Crear Mascota
        especie_perro = Especie.objects.create(nombre="Perro")
        raza_labrador = Raza.objects.create(nombre="Labrador", especie=especie_perro)

        self.mascota = Mascota.objects.create(
            nombre='Fido', 
            cliente=self.perfil_cliente, # Apunta al perfil del cliente
            especie=especie_perro, 
            raza=raza_labrador,
            sexo='M',
            fecha_nacimiento=timezone.now().date()
        )

        # 5. Crear Servicio
        self.servicio = Servicio.objects.create(nombre='Consulta Test', costo=100)

        # 6. Autenticar al cliente para todas las pruebas
        self.client.force_authenticate(user=self.cliente_user)
        
        # 7. Guardamos una fecha futura para usar en los tests
        self.fecha_futura = timezone.now() + timedelta(days=5, hours=10)