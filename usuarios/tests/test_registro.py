"""
Pruebas unitarias para el endpoint de registro de usuarios.

Autor: Jeronimo Rodríguez Sepúlveda
Fecha: 2025-11-10

Este módulo contiene las pruebas para el endpoint POST /api/v1/auth/register/,
que permite a los usuarios registrarse en el sistema como clientes.
"""

import pytest


@pytest.mark.django_db
class TestRegistroUsuario:
    """
    Clase de pruebas para el endpoint de registro de usuarios.
    
    Valida que el registro de nuevos usuarios funcione correctamente,
    incluyendo la creación del usuario, asignación de rol de cliente,
    y creación del perfil de cliente asociado.
    """
    
    def test_registro_exitoso(self, api_client, datos_registro_validos):
        """
        Prueba que un usuario se puede registrar exitosamente.
        
        Valida:
        - Código de respuesta 201 (CREATED)
        - Creación del usuario en la base de datos
        - Asignación automática del rol 'cliente'
        - Creación del perfil de cliente
        - Retorno de tokens JWT en la respuesta
        - Estructura correcta del JSON de respuesta
        """
        from django.urls import reverse
        from rest_framework import status
        from django.contrib.auth import get_user_model
        from usuarios.models import Rol, UsuarioRol, Cliente
        
        Usuario = get_user_model()
        url = reverse('registro')
        
        response = api_client.post(url, datos_registro_validos, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_201_CREATED
        
        # Validar estructura de la respuesta
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert 'message' in response.data
        
        # Validar datos del usuario en la respuesta
        user_data = response.data['user']
        assert user_data['username'] == datos_registro_validos['username']
        assert user_data['email'] == datos_registro_validos['email']
        assert user_data['nombre_completo'] == f"{datos_registro_validos['nombre']} {datos_registro_validos['apellido']}"
        
        # Validar tokens JWT
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert response.data['tokens']['access'] is not None
        assert response.data['tokens']['refresh'] is not None
        
        # Validar creación en base de datos
        usuario = Usuario.objects.get(username=datos_registro_validos['username'])
        assert usuario.email == datos_registro_validos['email']
        assert usuario.nombre == datos_registro_validos['nombre']
        assert usuario.apellido == datos_registro_validos['apellido']
        
        # Validar asignación de rol de cliente
        assert usuario.usuario_roles.filter(rol__nombre='cliente').exists()
        
        # Validar creación de perfil de cliente
        assert hasattr(usuario, 'perfil_cliente')
        assert usuario.perfil_cliente.telefono == datos_registro_validos['telefono']
        assert usuario.perfil_cliente.direccion == datos_registro_validos['direccion']
    
    def test_registro_contraseñas_no_coinciden(self, api_client, datos_registro_validos):
        """
        Prueba que el registro falla cuando las contraseñas no coinciden.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensaje de error apropiado
        - Usuario no se crea en la base de datos
        """
        from django.urls import reverse
        from rest_framework import status
        from django.contrib.auth import get_user_model
        
        Usuario = get_user_model()
        datos_registro_validos['password_confirm'] = 'PasswordDiferente123!'
        url = reverse('registro')
        
        response = api_client.post(url, datos_registro_validos, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar mensaje de error
        assert 'password_confirm' in response.data
        assert 'no coinciden' in str(response.data['password_confirm']).lower()
        
        # Validar que el usuario no se creó
        assert not Usuario.objects.filter(username=datos_registro_validos['username']).exists()
    
    def test_registro_email_duplicado(self, api_client, datos_registro_validos, usuario_cliente):
        """
        Prueba que el registro falla cuando el email ya existe.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensaje de error apropiado
        """
        from django.urls import reverse
        from rest_framework import status
        
        datos_registro_validos['email'] = usuario_cliente.email
        url = reverse('registro')
        
        response = api_client.post(url, datos_registro_validos, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar que hay un error relacionado con el email
        assert 'email' in response.data
    
    def test_registro_username_duplicado(self, api_client, datos_registro_validos, usuario_cliente):
        """
        Prueba que el registro falla cuando el username ya existe.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensaje de error apropiado
        """
        from django.urls import reverse
        from rest_framework import status
        
        datos_registro_validos['username'] = usuario_cliente.username
        url = reverse('registro')
        
        response = api_client.post(url, datos_registro_validos, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar que hay un error relacionado con el username
        assert 'username' in response.data
    
    def test_registro_campos_requeridos(self, api_client):
        """
        Prueba que el registro falla cuando faltan campos requeridos.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensajes de error para cada campo faltante
        """
        from django.urls import reverse
        from rest_framework import status
        
        url = reverse('registro')
        datos_vacios = {}
        
        response = api_client.post(url, datos_vacios, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar que hay errores para campos requeridos
        campos_requeridos = ['username', 'email', 'password', 'password_confirm', 'nombre', 'apellido']
        for campo in campos_requeridos:
            assert campo in response.data
    
    def test_registro_email_invalido(self, api_client, datos_registro_validos):
        """
        Prueba que el registro falla cuando el email tiene formato inválido.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensaje de error apropiado
        """
        from django.urls import reverse
        from rest_framework import status
        
        datos_registro_validos['email'] = 'email_invalido'
        url = reverse('registro')
        
        response = api_client.post(url, datos_registro_validos, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar que hay un error relacionado con el email
        assert 'email' in response.data
    
    def test_registro_campos_opcionales_perfil(self, api_client, datos_registro_validos):
        """
        Prueba que el registro funciona sin campos opcionales del perfil.
        
        Valida:
        - Código de respuesta 201 (CREATED)
        - Usuario se crea correctamente
        - Perfil de cliente se crea con valores vacíos para campos opcionales
        """
        from django.urls import reverse
        from rest_framework import status
        from django.contrib.auth import get_user_model
        
        Usuario = get_user_model()
        # Remover campos opcionales
        datos_registro_validos.pop('telefono', None)
        datos_registro_validos.pop('direccion', None)
        url = reverse('registro')
        
        response = api_client.post(url, datos_registro_validos, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_201_CREATED
        
        # Validar creación en base de datos
        usuario = Usuario.objects.get(username=datos_registro_validos['username'])
        assert hasattr(usuario, 'perfil_cliente')
        # Los campos opcionales pueden estar vacíos
        assert usuario.perfil_cliente.telefono == '' or usuario.perfil_cliente.telefono is None
        assert usuario.perfil_cliente.direccion == '' or usuario.perfil_cliente.direccion is None
    
    def test_registro_crea_rol_cliente_si_no_existe(self, api_client, datos_registro_validos, db):
        """
        Prueba que el registro crea el rol 'cliente' si no existe.
        
        Valida:
        - El rol 'cliente' se crea automáticamente si no existe
        - El usuario se asigna correctamente al rol creado
        """
        from django.urls import reverse
        from rest_framework import status
        from django.contrib.auth import get_user_model
        from usuarios.models import Rol
        
        Usuario = get_user_model()
        # Asegurar que el rol no existe
        Rol.objects.filter(nombre='cliente').delete()
        
        url = reverse('registro')
        response = api_client.post(url, datos_registro_validos, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_201_CREATED
        
        # Validar que el rol se creó
        assert Rol.objects.filter(nombre='cliente').exists()
        
        # Validar que el usuario tiene el rol
        usuario = Usuario.objects.get(username=datos_registro_validos['username'])
        assert usuario.usuario_roles.filter(rol__nombre='cliente').exists()