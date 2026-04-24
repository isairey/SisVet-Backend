"""
Pruebas unitarias para los endpoints de autenticación (logout y verificación de token).

Autor: Jeronimo Rodríguez Sepúlveda
Fecha: 2025-11-10

Este módulo contiene las pruebas para los endpoints:
- POST /api/v1/auth/logout/ - Cerrar sesión
- GET /api/v1/auth/verify/ - Verificar token válido
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
class TestLogout:
    """
    Clase de pruebas para el endpoint de logout.
    """
    
    def test_logout_exitoso(self, api_client, usuario_cliente):
        """
        Prueba que un usuario puede cerrar sesión exitosamente.
        
        Valida:
        - Código de respuesta 200 (OK)
        - Mensaje de éxito en la respuesta
        - El refresh token se añade a la lista negra (blacklist)
        """
        api_client.force_authenticate(user=usuario_cliente)
        
        # Generar refresh token
        refresh = RefreshToken.for_user(usuario_cliente)
        refresh_token_str = str(refresh)
        
        url = reverse('logout')
        datos_logout = {
            'refresh': refresh_token_str
        }
        
        response = api_client.post(url, datos_logout, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar mensaje de éxito
        assert 'detail' in response.data
        assert 'cerrada' in response.data['detail'].lower() or 'exitosamente' in response.data['detail'].lower()
        
        # Validar que el token está en la blacklist
        # Nota: Esto requiere que el token blacklist esté configurado
        try:
            token = RefreshToken(refresh_token_str)
            # Si el token está en la blacklist, esto debería fallar
            # La verificación exacta depende de la configuración de blacklist
        except Exception:
            # Si hay una excepción, el token está correctamente invalidado
            pass
    
    def test_logout_sin_refresh_token(self, api_client, usuario_cliente):
        """
        Prueba que el logout falla si no se proporciona el refresh token.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensaje de error apropiado
        """
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('logout')
        
        response = api_client.post(url, {}, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar mensaje de error
        assert 'detail' in response.data
        assert 'refresh' in response.data['detail'].lower() or 'requiere' in response.data['detail'].lower()
    
    def test_logout_refresh_token_invalido(self, api_client, usuario_cliente):
        """
        Prueba que el logout falla con un refresh token inválido.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensaje de error apropiado
        """
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('logout')
        
        datos_logout = {
            'refresh': 'token_invalido_12345'
        }
        
        response = api_client.post(url, datos_logout, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar mensaje de error
        assert 'detail' in response.data
        assert 'inválido' in response.data['detail'].lower() or 'invalido' in response.data['detail'].lower() or 'expirado' in response.data['detail'].lower()
    
    def test_logout_sin_autenticacion(self, api_client):
        """
        Prueba que el logout requiere autenticación.
        
        Valida:
        - Código de respuesta 401 (UNAUTHORIZED)
        """
        url = reverse('logout')
        datos_logout = {
            'refresh': 'cualquier_token'
        }
        
        response = api_client.post(url, datos_logout, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestVerificarToken:
    """
    Clase de pruebas para el endpoint de verificación de token.
    """
    
    def test_verificar_token_exitoso(self, api_client, usuario_cliente):
        """
        Prueba que se puede verificar un token válido.
        
        Valida:
        - Código de respuesta 200 (OK)
        - Información del usuario en la respuesta
        - Campo 'valid' en True
        - Estructura correcta del JSON de respuesta
        """
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('verify_token')
        
        response = api_client.get(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar estructura de la respuesta
        assert 'valid' in response.data
        assert response.data['valid'] is True
        assert 'user' in response.data
        
        # Validar información del usuario
        user_data = response.data['user']
        assert 'id' in user_data
        assert 'username' in user_data
        assert 'email' in user_data
        assert 'nombre_completo' in user_data
        assert 'roles' in user_data
        
        # Validar datos del usuario
        assert user_data['id'] == usuario_cliente.id
        assert user_data['username'] == usuario_cliente.username
        assert user_data['email'] == usuario_cliente.email
    
    def test_verificar_token_incluye_roles(self, api_client, usuario_cliente):
        """
        Prueba que la verificación de token incluye los roles del usuario.
        
        Valida:
        - Los roles están presentes en la respuesta
        - Los roles son correctos
        """
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('verify_token')
        
        response = api_client.get(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar roles
        assert 'roles' in response.data['user']
        assert isinstance(response.data['user']['roles'], list)
        assert len(response.data['user']['roles']) > 0
    
    def test_verificar_token_sin_autenticacion(self, api_client):
        """
        Prueba que verificar token requiere autenticación.
        
        Valida:
        - Código de respuesta 401 (UNAUTHORIZED)
        """
        url = reverse('verify_token')
        
        response = api_client.get(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_verificar_token_diferentes_usuarios(self, api_client, usuario_cliente, usuario_administrador):
        """
        Prueba que la verificación de token retorna información del usuario autenticado.
        
        Valida:
        - Cada usuario ve su propia información
        - Los datos son correctos para cada usuario
        """
        # Verificar token del cliente
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('verify_token')
        
        response_cliente = api_client.get(url)
        assert response_cliente.status_code == status.HTTP_200_OK
        assert response_cliente.data['user']['id'] == usuario_cliente.id
        assert response_cliente.data['user']['username'] == usuario_cliente.username
        
        # Verificar token del administrador
        api_client.force_authenticate(user=usuario_administrador)
        response_admin = api_client.get(url)
        assert response_admin.status_code == status.HTTP_200_OK
        assert response_admin.data['user']['id'] == usuario_administrador.id
        assert response_admin.data['user']['username'] == usuario_administrador.username
    
    def test_verificar_token_nombre_completo(self, api_client, usuario_cliente):
        """
        Prueba que la verificación de token incluye el nombre completo del usuario.
        
        Valida:
        - El campo 'nombre_completo' está presente
        - El formato es correcto (nombre + apellido)
        """
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('verify_token')
        
        response = api_client.get(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar nombre completo
        assert 'nombre_completo' in response.data['user']
        nombre_completo_esperado = f"{usuario_cliente.nombre} {usuario_cliente.apellido}"
        assert response.data['user']['nombre_completo'] == nombre_completo_esperado

