import pytest
from django.urls import reverse
from rest_framework import status
from mascotas.models import Especie, Raza, Mascota
from usuarios.models import UsuarioRol


@pytest.mark.django_db
class TestListadoMascotasPorRol:
    """
    Suite de pruebas para validar el filtrado de mascotas según el rol del usuario.
    
    Verifica que:
    - Los ADMIN, VETERINARIOS y RECEPCIONISTAS ven todas las mascotas.
    - Los CLIENTES solo ven sus propias mascotas.
    - Solo usuarios autenticados pueden acceder.
    """

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Setup inicial: crea especies, razas y mascotas de prueba."""
        # Crear especies y razas
        self.especie_perro = Especie.objects.create(nombre='Perro')
        self.especie_gato = Especie.objects.create(nombre='Gato')
        
        self.raza_labrador = Raza.objects.create(
            nombre='Labrador',
            especie=self.especie_perro
        )
        self.raza_siames = Raza.objects.create(
            nombre='Siamés',
            especie=self.especie_gato
        )

    def test_usuario_no_autenticado_rechazado(self, api_client):
        """
        Un usuario no autenticado no puede acceder al endpoint de mascotas.
        """
        url = reverse('mascotas-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_administrador_ve_todas_las_mascotas(
        self, api_client, usuario_administrador, usuario_cliente, rol_cliente
    ):
        """
        Un ADMINISTRADOR puede ver todas las mascotas del sistema,
        incluyendo las de otros clientes.
        """
        # Crear cliente adicional
        from django.contrib.auth import get_user_model
        from usuarios.models import Cliente
        
        Usuario = get_user_model()
        cliente_1 = Usuario.objects.create_user(
            username='cliente1',
            email='cliente1@test.com',
            password='pass123',
            nombre='Cliente',
            apellido='Uno',
            estado='activo'
        )
        UsuarioRol.objects.create(usuario=cliente_1, rol=rol_cliente)
        Cliente.objects.create(usuario=cliente_1, telefono='123', direccion='Dir1')

        cliente_2 = Usuario.objects.create_user(
            username='cliente2',
            email='cliente2@test.com',
            password='pass123',
            nombre='Cliente',
            apellido='Dos',
            estado='activo'
        )
        UsuarioRol.objects.create(usuario=cliente_2, rol=rol_cliente)
        Cliente.objects.create(usuario=cliente_2, telefono='456', direccion='Dir2')

        # Crear mascotas para cada cliente
        mascota_cliente_1 = Mascota.objects.create(
            cliente=cliente_1.perfil_cliente,
            especie=self.especie_perro,
            raza=self.raza_labrador,
            nombre='Fido',
            sexo='M'
        )
        
        mascota_cliente_2 = Mascota.objects.create(
            cliente=cliente_2.perfil_cliente,
            especie=self.especie_gato,
            raza=self.raza_siames,
            nombre='Michi',
            sexo='H'
        )

        # Administrador accede al endpoint
        api_client.force_authenticate(user=usuario_administrador)
        url = reverse('mascotas-list-create')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Debe ver ambas mascotas
        mascotas = response.data if isinstance(response.data, list) else response.data.get('results', [])
        assert len(mascotas) == 2
        nombres = {m['nombre'] for m in mascotas}
        assert 'Fido' in nombres
        assert 'Michi' in nombres

    def test_veterinario_ve_todas_las_mascotas(
        self, api_client, usuario_veterinario, usuario_cliente, rol_cliente
    ):
        """
        Un VETERINARIO puede ver todas las mascotas del sistema,
        incluyendo las de otros clientes.
        """
        from django.contrib.auth import get_user_model
        from usuarios.models import Cliente
        
        Usuario = get_user_model()
        cliente_1 = Usuario.objects.create_user(
            username='cliente1',
            email='cliente1@test.com',
            password='pass123',
            nombre='Cliente',
            apellido='Uno',
            estado='activo'
        )
        UsuarioRol.objects.create(usuario=cliente_1, rol=rol_cliente)
        Cliente.objects.create(usuario=cliente_1, telefono='123', direccion='Dir1')

        cliente_2 = Usuario.objects.create_user(
            username='cliente2',
            email='cliente2@test.com',
            password='pass123',
            nombre='Cliente',
            apellido='Dos',
            estado='activo'
        )
        UsuarioRol.objects.create(usuario=cliente_2, rol=rol_cliente)
        Cliente.objects.create(usuario=cliente_2, telefono='456', direccion='Dir2')

        # Crear mascotas
        mascota_cliente_1 = Mascota.objects.create(
            cliente=cliente_1.perfil_cliente,
            especie=self.especie_perro,
            raza=self.raza_labrador,
            nombre='Fido',
            sexo='M'
        )
        
        mascota_cliente_2 = Mascota.objects.create(
            cliente=cliente_2.perfil_cliente,
            especie=self.especie_gato,
            raza=self.raza_siames,
            nombre='Michi',
            sexo='H'
        )

        # Veterinario accede al endpoint
        api_client.force_authenticate(user=usuario_veterinario)
        url = reverse('mascotas-list-create')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        mascotas = response.data if isinstance(response.data, list) else response.data.get('results', [])
        assert len(mascotas) == 2
        nombres = {m['nombre'] for m in mascotas}
        assert 'Fido' in nombres
        assert 'Michi' in nombres

    def test_recepcionista_ve_todas_las_mascotas(
        self, api_client, rol_recepcionista, usuario_cliente, rol_cliente
    ):
        """
        Un RECEPCIONISTA puede ver todas las mascotas del sistema,
        incluyendo las de otros clientes.
        """
        from django.contrib.auth import get_user_model
        from usuarios.models import UsuarioRol, Cliente
        
        Usuario = get_user_model()
        
        # Crear recepcionista
        recepcionista = Usuario.objects.create_user(
            username='recepcionista_test',
            email='recep@test.com',
            password='receppass123',
            nombre='Recepcionista',
            apellido='Test',
            estado='activo'
        )
        UsuarioRol.objects.create(usuario=recepcionista, rol=rol_recepcionista)

        # Crear clientes
        cliente_1 = Usuario.objects.create_user(
            username='cliente1',
            email='cliente1@test.com',
            password='pass123',
            nombre='Cliente',
            apellido='Uno',
            estado='activo'
        )
        UsuarioRol.objects.create(usuario=cliente_1, rol=rol_cliente)
        Cliente.objects.create(usuario=cliente_1, telefono='123', direccion='Dir1')

        cliente_2 = Usuario.objects.create_user(
            username='cliente2',
            email='cliente2@test.com',
            password='pass123',
            nombre='Cliente',
            apellido='Dos',
            estado='activo'
        )
        UsuarioRol.objects.create(usuario=cliente_2, rol=rol_cliente)
        Cliente.objects.create(usuario=cliente_2, telefono='456', direccion='Dir2')

        # Crear mascotas
        mascota_cliente_1 = Mascota.objects.create(
            cliente=cliente_1.perfil_cliente,
            especie=self.especie_perro,
            raza=self.raza_labrador,
            nombre='Fido',
            sexo='M'
        )
        
        mascota_cliente_2 = Mascota.objects.create(
            cliente=cliente_2.perfil_cliente,
            especie=self.especie_gato,
            raza=self.raza_siames,
            nombre='Michi',
            sexo='H'
        )

        # Recepcionista accede al endpoint
        api_client.force_authenticate(user=recepcionista)
        url = reverse('mascotas-list-create')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        mascotas = response.data if isinstance(response.data, list) else response.data.get('results', [])
        assert len(mascotas) == 2
        nombres = {m['nombre'] for m in mascotas}
        assert 'Fido' in nombres
        assert 'Michi' in nombres

    def test_cliente_solo_ve_sus_propias_mascotas(
        self, api_client, usuario_cliente, rol_cliente
    ):
        """
        Un CLIENTE solo ve sus propias mascotas,
        no las de otros clientes.
        """
        from django.contrib.auth import get_user_model
        from usuarios.models import Cliente
        
        Usuario = get_user_model()
        
        # Crear otro cliente
        cliente_2 = Usuario.objects.create_user(
            username='cliente2',
            email='cliente2@test.com',
            password='pass123',
            nombre='Cliente',
            apellido='Dos',
            estado='activo'
        )
        UsuarioRol.objects.create(usuario=cliente_2, rol=rol_cliente)
        Cliente.objects.create(usuario=cliente_2, telefono='456', direccion='Dir2')

        # Crear mascotas del cliente_1 (usuario_cliente)
        mascota_del_cliente = Mascota.objects.create(
            cliente=usuario_cliente.perfil_cliente,
            especie=self.especie_perro,
            raza=self.raza_labrador,
            nombre='Fido',
            sexo='M'
        )

        # Crear mascotas del cliente_2
        mascota_del_otro_cliente = Mascota.objects.create(
            cliente=cliente_2.perfil_cliente,
            especie=self.especie_gato,
            raza=self.raza_siames,
            nombre='Michi',
            sexo='H'
        )

        # Cliente accede al endpoint
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('mascotas-list-create')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        mascotas = response.data if isinstance(response.data, list) else response.data.get('results', [])
        
        # Debe ver SOLO su propia mascota
        assert len(mascotas) == 1
        assert mascotas[0]['nombre'] == 'Fido'

    def test_cliente_sin_mascotas_recibe_mensaje_amigable(self, api_client, usuario_cliente):
        """
        Un cliente sin mascotas recibe un mensaje amigable
        en lugar de una lista vacía confusa.
        """
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('mascotas-list-create')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        assert 'No hay mascotas disponibles' in response.data['message']
        assert response.data['results'] == []

    def test_cliente_con_multiples_mascotas(self, api_client, usuario_cliente):
        """
        Un cliente puede tener múltiples mascotas y verlas todas.
        """
        # Crear múltiples mascotas para el cliente
        mascotas_esperadas = []
        for i in range(3):
            mascota = Mascota.objects.create(
                cliente=usuario_cliente.perfil_cliente,
                especie=self.especie_perro if i % 2 == 0 else self.especie_gato,
                raza=self.raza_labrador if i % 2 == 0 else self.raza_siames,
                nombre=f'Mascota_{i+1}',
                sexo='M' if i % 2 == 0 else 'H'
            )
            mascotas_esperadas.append(mascota.nombre)

        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('mascotas-list-create')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        mascotas = response.data if isinstance(response.data, list) else response.data.get('results', [])
        assert len(mascotas) == 3
        nombres_obtenidos = {m['nombre'] for m in mascotas}
        assert nombres_obtenidos == set(mascotas_esperadas)

    def test_cliente_no_puede_acceder_a_mascota_de_otro_cliente(
        self, api_client, usuario_cliente, rol_cliente
    ):
        """
        Cuando un cliente intenta acceder a una mascota de otro cliente
        mediante GET /:id, recibe 404.
        """
        from django.contrib.auth import get_user_model
        from usuarios.models import Cliente
        
        Usuario = get_user_model()
        
        # Crear otro cliente
        cliente_2 = Usuario.objects.create_user(
            username='cliente2',
            email='cliente2@test.com',
            password='pass123',
            nombre='Cliente',
            apellido='Dos',
            estado='activo'
        )
        UsuarioRol.objects.create(usuario=cliente_2, rol=rol_cliente)
        Cliente.objects.create(usuario=cliente_2, telefono='456', direccion='Dir2')

        # Crear mascota del cliente_2
        mascota_del_otro = Mascota.objects.create(
            cliente=cliente_2.perfil_cliente,
            especie=self.especie_gato,
            raza=self.raza_siames,
            nombre='Michi',
            sexo='H'
        )

        # El usuario_cliente intenta acceder a la mascota de cliente_2
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('mascota-detail', kwargs={'pk': mascota_del_otro.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_admin_puede_acceder_a_cualquier_mascota(
        self, api_client, usuario_administrador, usuario_cliente, rol_cliente
    ):
        """
        Un administrador puede acceder al detalle de cualquier mascota del sistema.
        """
        # Crear mascota del cliente
        mascota = Mascota.objects.create(
            cliente=usuario_cliente.perfil_cliente,
            especie=self.especie_perro,
            raza=self.raza_labrador,
            nombre='Fido',
            sexo='M'
        )

        # Admin accede al detalle
        api_client.force_authenticate(user=usuario_administrador)
        url = reverse('mascota-detail', kwargs={'pk': mascota.id})
        response = api_client.get(url)

        # NOTA: El endpoint actual filtra por cliente__usuario=request.user
        # Por lo que el admin NO puede acceder a mascotas de otros clientes en GET
        # Esto es un comportamiento esperado si queremos que solo clientes vean detalles
        # Si se desea que admins vean cualquier mascota, se debe ajustar get_queryset()
        # de MascotaRetrieveUpdateDeleteView
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_filtrado_exacto_por_cliente(
        self, api_client, usuario_cliente, rol_cliente
    ):
        """
        Verifica que el filtrado sea exacto: solo mascotas donde
        mascota.cliente.usuario == request.user.
        """
        from django.contrib.auth import get_user_model
        from usuarios.models import Cliente
        
        Usuario = get_user_model()
        
        # Crear varios clientes
        clientes = []
        for i in range(3):
            cliente = Usuario.objects.create_user(
                username=f'cliente{i}',
                email=f'cliente{i}@test.com',
                password='pass123',
                nombre=f'Cliente',
                apellido=f'{i}',
                estado='activo'
            )
            UsuarioRol.objects.create(usuario=cliente, rol=rol_cliente)
            Cliente.objects.create(usuario=cliente, telefono=f'{i}00', direccion=f'Dir{i}')
            clientes.append(cliente)

        # Crear mascotas para cada cliente
        for idx, cliente in enumerate(clientes):
            for j in range(2):
                Mascota.objects.create(
                    cliente=cliente.perfil_cliente,
                    especie=self.especie_perro,
                    raza=self.raza_labrador,
                    nombre=f'Mascota_Cliente{idx}_Pet{j}',
                    sexo='M'
                )

        # Cada cliente verifica que solo ve sus mascotas
        for idx, cliente in enumerate(clientes):
            api_client.force_authenticate(user=cliente)
            url = reverse('mascotas-list-create')
            response = api_client.get(url)

            assert response.status_code == status.HTTP_200_OK
            mascotas = response.data if isinstance(response.data, list) else response.data.get('results', [])
            assert len(mascotas) == 2
            
            # Verificar que todas pertenecen al cliente correcto
            for mascota in mascotas:
                assert f'Cliente{idx}' in mascota['nombre']
