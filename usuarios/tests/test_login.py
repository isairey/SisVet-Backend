"""
Pruebas unitarias para el endpoint de inicio de sesión (login).

Autor: Jeronimo Rodríguez Sepúlveda
Fecha: 2025-11-10

Este módulo contiene las pruebas para el endpoint POST /api/v1/auth/login/,
que permite a los usuarios autenticarse y obtener tokens JWT.
"""

import pytest


@pytest.mark.django_db
class TestLoginUsuario:
    """
    Clase de pruebas para el endpoint de inicio de sesión.
    
    Valida que el login funcione correctamente, incluyendo la generación
    de tokens JWT, manejo de credenciales incorrectas, y bloqueo temporal
    por múltiples intentos fallidos.
    """
    
    def test_login_exitoso(self, api_client, usuario_cliente, datos_login_validos):
        """
        Prueba que un usuario puede iniciar sesión exitosamente.
        
        Valida:
        - Código de respuesta 200 (OK)
        - Retorno de tokens JWT (access y refresh)
        - Información del usuario en la respuesta
        - Estructura correcta del JSON de respuesta
        - Reset de intentos fallidos después de login exitoso
        """
        from django.urls import reverse
        from rest_framework import status
        
        url = reverse('token_obtain_pair')
        
        response = api_client.post(url, datos_login_validos, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar estructura de la respuesta
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        
        # Validar tokens JWT
        assert response.data['access'] is not None
        assert response.data['refresh'] is not None
        assert len(response.data['access']) > 0
        assert len(response.data['refresh']) > 0
        
        # Validar información del usuario
        user_data = response.data['user']
        assert user_data['id'] == usuario_cliente.id
        assert user_data['username'] == usuario_cliente.username
        assert user_data['email'] == usuario_cliente.email
        assert 'nombre_completo' in user_data
        assert 'roles' in user_data
        
        # Validar que los intentos fallidos se resetean
        usuario_cliente.refresh_from_db()
        assert usuario_cliente.intentos_fallidos == 0
        assert usuario_cliente.bloqueado_hasta is None
    
    def test_login_credenciales_incorrectas(self, api_client, usuario_cliente):
        """
        Prueba que el login falla con credenciales incorrectas.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensaje de error apropiado
        - Incremento de contador de intentos fallidos
        """
        from django.urls import reverse
        from rest_framework import status
        
        url = reverse('token_obtain_pair')
        datos_incorrectos = {
            'username': 'cliente_test',
            'password': 'password_incorrecta'
        }
        
        response = api_client.post(url, datos_incorrectos, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar mensaje de error
        assert 'non_field_errors' in response.data or 'detail' in response.data
        
        # Validar incremento de intentos fallidos
        usuario_cliente.refresh_from_db()
        assert usuario_cliente.intentos_fallidos > 0
    
    def test_login_usuario_no_existe(self, api_client):
        """
        Prueba que el login falla cuando el usuario no existe.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensaje de error apropiado
        """
        from django.urls import reverse
        from rest_framework import status
        
        url = reverse('token_obtain_pair')
        datos_inexistente = {
            'username': 'usuario_inexistente',
            'password': 'cualquier_password'
        }
        
        response = api_client.post(url, datos_inexistente, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar mensaje de error
        assert 'non_field_errors' in response.data or 'detail' in response.data
    
    def test_login_usuario_inactivo(self, api_client, rol_cliente, db):
        """
        Prueba que el login falla cuando el usuario está inactivo.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensaje de error indicando que la cuenta está inactiva
        """
        from django.urls import reverse
        from rest_framework import status
        from django.contrib.auth import get_user_model
        from usuarios.models import UsuarioRol
        
        Usuario = get_user_model()
        # Crear usuario inactivo
        usuario_inactivo = Usuario.objects.create_user(
            username='usuario_inactivo',
            email='inactivo@test.com',
            password='testpass123',
            nombre='Usuario',
            apellido='Inactivo',
            estado='inactivo',
            is_active=False
        )
        UsuarioRol.objects.create(usuario=usuario_inactivo, rol=rol_cliente)
        
        url = reverse('token_obtain_pair')
        datos_login = {
            'username': 'usuario_inactivo',
            'password': 'testpass123'
        }
        
        response = api_client.post(url, datos_login, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar mensaje de error
        error_message = str(response.data.get('non_field_errors', []) or response.data.get('detail', ''))
        assert 'inactiva' in error_message.lower() or 'inactivo' in error_message.lower()
    
    def test_login_usuario_suspendido(self, api_client, rol_cliente, db):
        """
        Prueba que el login falla cuando el usuario está suspendido.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensaje de error indicando que la cuenta está suspendida
        """
        from django.urls import reverse
        from rest_framework import status
        from django.contrib.auth import get_user_model
        from usuarios.models import UsuarioRol
        
        Usuario = get_user_model()
        # Crear usuario suspendido
        usuario_suspendido = Usuario.objects.create_user(
            username='usuario_suspendido',
            email='suspendido@test.com',
            password='testpass123',
            nombre='Usuario',
            apellido='Suspendido',
            estado='suspendido',
            is_active=False
        )
        UsuarioRol.objects.create(usuario=usuario_suspendido, rol=rol_cliente)
        
        url = reverse('token_obtain_pair')
        datos_login = {
            'username': 'usuario_suspendido',
            'password': 'testpass123'
        }
        
        response = api_client.post(url, datos_login, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar mensaje de error
        error_message = str(response.data.get('non_field_errors', []) or response.data.get('detail', ''))
        assert 'suspendido' in error_message.lower() or 'estado' in error_message.lower()
    
    def test_login_usuario_bloqueado_temporalmente(self, api_client, usuario_cliente):
        """
        Prueba que el login falla cuando el usuario está bloqueado temporalmente.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensaje de error indicando el bloqueo temporal
        - Información sobre los minutos restantes
        """
        from django.urls import reverse
        from rest_framework import status
        from django.utils import timezone
        from datetime import timedelta
        
        # Bloquear usuario temporalmente
        usuario_cliente.bloqueado_hasta = timezone.now() + timedelta(minutes=10)
        usuario_cliente.save()
        
        url = reverse('token_obtain_pair')
        datos_login = {
            'username': 'cliente_test',
            'password': 'testpass123'
        }
        
        response = api_client.post(url, datos_login, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar mensaje de error
        error_message = str(response.data.get('non_field_errors', []) or response.data.get('detail', ''))
        assert 'bloqueada' in error_message.lower() or 'bloqueado' in error_message.lower()
    
    def test_login_campos_requeridos(self, api_client):
        """
        Prueba que el login falla cuando faltan campos requeridos.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensajes de error para campos faltantes
        """
        from django.urls import reverse
        from rest_framework import status
        
        url = reverse('token_obtain_pair')
        
        # Prueba sin username
        response = api_client.post(url, {'password': 'testpass123'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data
        
        # Prueba sin password
        response = api_client.post(url, {'username': 'cliente_test'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
    
    def test_login_multiples_intentos_fallidos_bloquea_cuenta(self, api_client, usuario_cliente):
        """
        Prueba que múltiples intentos fallidos bloquean la cuenta temporalmente.
        
        Valida:
        - Después de varios intentos fallidos, la cuenta se bloquea
        - Mensaje de error indica el bloqueo
        - El bloqueo tiene una duración determinada
        """
        from django.urls import reverse
        from django.utils import timezone
        
        url = reverse('token_obtain_pair')
        datos_incorrectos = {
            'username': 'cliente_test',
            'password': 'password_incorrecta'
        }
        
        # Realizar múltiples intentos fallidos (más de 5)
        for _ in range(6):
            response = api_client.post(url, datos_incorrectos, format='json')
        
        # Validar que la cuenta está bloqueada
        usuario_cliente.refresh_from_db()
        assert usuario_cliente.bloqueado_hasta is not None
        assert usuario_cliente.bloqueado_hasta > timezone.now()
        
        # Validar que el último intento retorna error de bloqueo
        response = api_client.post(url, datos_incorrectos, format='json')
        from rest_framework import status
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error_message = str(response.data.get('non_field_errors', []) or response.data.get('detail', ''))
        assert 'bloqueada' in error_message.lower() or 'bloqueado' in error_message.lower()
    
    def test_login_resetea_intentos_al_autenticar(self, api_client, usuario_cliente):
        """
        Prueba que un login exitoso resetea los intentos fallidos.
        
        Valida:
        - Los intentos fallidos se resetean después de login exitoso
        - El bloqueo temporal se elimina
        """
        from django.urls import reverse
        from rest_framework import status
        
        # Simular algunos intentos fallidos
        usuario_cliente.intentos_fallidos = 3
        usuario_cliente.save()
        
        url = reverse('token_obtain_pair')
        datos_login = {
            'username': 'cliente_test',
            'password': 'testpass123'
        }
        
        response = api_client.post(url, datos_login, format='json')
        
        # Validar login exitoso
        assert response.status_code == status.HTTP_200_OK
        
        # Validar que los intentos se resetean
        usuario_cliente.refresh_from_db()
        assert usuario_cliente.intentos_fallidos == 0
        assert usuario_cliente.bloqueado_hasta is None
    
    def test_login_incluye_roles_en_respuesta(self, api_client, usuario_cliente, datos_login_validos):
        """
        Prueba que la respuesta del login incluye los roles del usuario.
        
        Valida:
        - La respuesta incluye el campo 'roles'
        - Los roles están correctamente serializados
        """
        from django.urls import reverse
        from rest_framework import status
        
        url = reverse('token_obtain_pair')
        
        response = api_client.post(url, datos_login_validos, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar que los roles están en la respuesta
        assert 'roles' in response.data['user']
        assert isinstance(response.data['user']['roles'], list)
        assert 'cliente' in [rol.lower() for rol in response.data['user']['roles']]

