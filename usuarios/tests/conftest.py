"""
Configuración compartida y fixtures para las pruebas unitarias.

Autor: Jeronimo Rodríguez Sepúlveda
Fecha: 2025-11-10

Este archivo contiene fixtures reutilizables que se utilizan en múltiples
archivos de pruebas para evitar duplicación de código.
"""

import pytest


@pytest.fixture
def api_client():
    """
    Fixture que proporciona un cliente API para realizar peticiones HTTP.
    
    Este cliente se utiliza para simular peticiones a los endpoints
    de la API sin necesidad de levantar un servidor real.
    """
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def rol_cliente(db):
    """
    Fixture que crea y retorna el rol 'cliente' en la base de datos.
    
    Si el rol ya existe, lo retorna sin crear uno nuevo.
    """
    from usuarios.models import Rol
    rol, _ = Rol.objects.get_or_create(nombre='cliente')
    return rol


@pytest.fixture
def rol_administrador(db):
    """
    Fixture que crea y retorna el rol 'administrador' en la base de datos.
    
    Si el rol ya existe, lo retorna sin crear uno nuevo.
    """
    from usuarios.models import Rol
    rol, _ = Rol.objects.get_or_create(nombre='administrador')
    return rol


@pytest.fixture
def rol_veterinario(db):
    """
    Fixture que crea y retorna el rol 'veterinario' en la base de datos.
    
    Si el rol ya existe, lo retorna sin crear uno nuevo.
    """
    from usuarios.models import Rol
    rol, _ = Rol.objects.get_or_create(nombre='veterinario')
    return rol


@pytest.fixture
def rol_recepcionista(db):
    """
    Fixture que crea y retorna el rol 'recepcionista' en la base de datos.
    
    Si el rol ya existe, lo retorna sin crear uno nuevo.
    """
    from usuarios.models import Rol
    rol, _ = Rol.objects.get_or_create(nombre='recepcionista')
    return rol


@pytest.fixture
def usuario_cliente(db, rol_cliente):
    """
    Fixture que crea y retorna un usuario con rol de cliente.
    
    Este usuario se utiliza para pruebas que requieren un usuario
    autenticado con permisos de cliente.
    """
    from django.contrib.auth import get_user_model
    from usuarios.models import UsuarioRol, Cliente
    
    Usuario = get_user_model()
    usuario = Usuario.objects.create_user(
        username='cliente_test',
        email='cliente@test.com',
        password='testpass123',
        nombre='Cliente',
        apellido='Test',
        estado='activo'
    )
    UsuarioRol.objects.create(usuario=usuario, rol=rol_cliente)
    Cliente.objects.create(
        usuario=usuario,
        telefono='1234567890',
        direccion='Dirección de prueba'
    )
    return usuario


@pytest.fixture
def usuario_administrador(db, rol_administrador):
    """
    Fixture que crea y retorna un usuario con rol de administrador.
    
    Este usuario se utiliza para pruebas que requieren permisos
    de administrador.
    """
    from django.contrib.auth import get_user_model
    from usuarios.models import UsuarioRol
    
    Usuario = get_user_model()
    usuario = Usuario.objects.create_user(
        username='admin_test',
        email='admin@test.com',
        password='adminpass123',
        nombre='Admin',
        apellido='Test',
        estado='activo'
    )
    UsuarioRol.objects.create(usuario=usuario, rol=rol_administrador)
    return usuario


@pytest.fixture
def usuario_veterinario(db, rol_veterinario):
    """
    Fixture que crea y retorna un usuario con rol de veterinario.
    
    Este usuario incluye el perfil de veterinario con licencia
    y especialidad.
    """
    from django.contrib.auth import get_user_model
    from usuarios.models import UsuarioRol, Veterinario
    
    Usuario = get_user_model()
    usuario = Usuario.objects.create_user(
        username='vet_test',
        email='vet@test.com',
        password='vetpass123',
        nombre='Veterinario',
        apellido='Test',
        estado='activo'
    )
    UsuarioRol.objects.create(usuario=usuario, rol=rol_veterinario)
    Veterinario.objects.create(
        usuario=usuario,
        licencia='LIC123456',
        especialidad='Cirugía',
        horario='Lunes a Viernes 8:00 - 17:00'
    )
    return usuario


@pytest.fixture
def usuario_recepcionista(db, rol_recepcionista):
    """
    Fixture que crea y retorna un usuario con rol de recepcionista.
    
    Este usuario se utiliza para pruebas que requieren permisos
    de recepcionista.
    """
    from django.contrib.auth import get_user_model
    from usuarios.models import UsuarioRol
    
    Usuario = get_user_model()
    usuario = Usuario.objects.create_user(
        username='recep_test',
        email='recep@test.com',
        password='receppass123',
        nombre='Recepcionista',
        apellido='Test',
        estado='activo'
    )
    UsuarioRol.objects.create(usuario=usuario, rol=rol_recepcionista)
    return usuario


@pytest.fixture
def usuario_autenticado(api_client, usuario_cliente):
    """
    Fixture que autentica un usuario cliente y retorna el cliente API.
    
    Este fixture es útil para pruebas que requieren un usuario
    autenticado pero no necesitan permisos específicos.
    """
    api_client.force_authenticate(user=usuario_cliente)
    return api_client


@pytest.fixture
def usuario_admin_autenticado(api_client, usuario_administrador):
    """
    Fixture que autentica un usuario administrador y retorna el cliente API.
    
    Este fixture es útil para pruebas que requieren permisos
    de administrador.
    """
    api_client.force_authenticate(user=usuario_administrador)
    return api_client


@pytest.fixture
def datos_registro_validos():
    """
    Fixture que retorna un diccionario con datos válidos para registro.
    
    Estos datos pueden ser utilizados directamente en peticiones POST
    al endpoint de registro.
    """
    return {
        'username': 'nuevo_usuario',
        'email': 'nuevo@test.com',
        'password': 'TestPass123!',
        'password_confirm': 'TestPass123!',
        'nombre': 'Nuevo',
        'apellido': 'Usuario',
        'telefono': '9876543210',
        'direccion': 'Nueva Dirección'
    }


@pytest.fixture
def datos_login_validos(usuario_cliente):
    """
    Fixture que retorna un diccionario con credenciales válidas para login.
    
    Utiliza el usuario_cliente creado por el fixture correspondiente.
    """
    return {
        'username': 'cliente_test',
        'password': 'testpass123'
    }

