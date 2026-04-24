"""
Pruebas unitarias para el endpoint de cambio de contraseña.

Autor: Jeronimo Rodríguez Sepúlveda
Fecha: 2025-11-10

Este módulo contiene las pruebas para el endpoint POST /api/v1/usuarios/{id}/cambiar_password/,
que permite a los usuarios cambiar su contraseña.
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status

Usuario = get_user_model()


@pytest.mark.django_db
class TestCambioPassword:
    """
    Clase de pruebas para el endpoint de cambio de contraseña.
    
    Valida que los usuarios puedan cambiar su contraseña correctamente,
    incluyendo validaciones de seguridad y manejo de errores.
    """
    
    def test_cambio_password_exitoso(self, api_client, usuario_cliente):
        """
        Prueba que un usuario puede cambiar su contraseña exitosamente.
        
        Valida:
        - Código de respuesta 200 (OK)
        - Mensaje de éxito en la respuesta
        - La nueva contraseña funciona para login
        - La contraseña anterior ya no funciona
        """
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('usuario-cambiar-password', kwargs={'pk': usuario_cliente.id})
        
        datos_cambio = {
            'password_actual': 'testpass123',
            'password_nueva': 'NuevaPassword123!',
            'password_nueva_confirm': 'NuevaPassword123!'
        }
        
        response = api_client.post(url, datos_cambio, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar mensaje de éxito
        assert 'detail' in response.data
        assert 'actualizada' in response.data['detail'].lower() or 'correctamente' in response.data['detail'].lower()
        
        # Validar que la nueva contraseña funciona
        usuario_cliente.refresh_from_db()
        assert usuario_cliente.check_password('NuevaPassword123!')
        
        # Validar que la contraseña anterior ya no funciona
        assert not usuario_cliente.check_password('testpass123')
    
    def test_cambio_password_contraseña_actual_incorrecta(self, api_client, usuario_cliente):
        """
        Prueba que el cambio de contraseña falla si la contraseña actual es incorrecta.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensaje de error indicando contraseña actual incorrecta
        - La contraseña no se modifica
        """
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('usuario-cambiar-password', kwargs={'pk': usuario_cliente.id})
        
        datos_cambio = {
            'password_actual': 'password_incorrecta',
            'password_nueva': 'NuevaPassword123!',
            'password_nueva_confirm': 'NuevaPassword123!'
        }
        
        response = api_client.post(url, datos_cambio, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar mensaje de error
        assert 'password_actual' in response.data
        error_message = str(response.data['password_actual'])
        assert 'incorrecta' in error_message.lower()
        
        # Validar que la contraseña no se modificó
        usuario_cliente.refresh_from_db()
        assert usuario_cliente.check_password('testpass123')
    
    def test_cambio_password_contraseñas_nuevas_no_coinciden(self, api_client, usuario_cliente):
        """
        Prueba que el cambio de contraseña falla si las contraseñas nuevas no coinciden.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensaje de error indicando que las contraseñas no coinciden
        - La contraseña no se modifica
        """
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('usuario-cambiar-password', kwargs={'pk': usuario_cliente.id})
        
        datos_cambio = {
            'password_actual': 'testpass123',
            'password_nueva': 'NuevaPassword123!',
            'password_nueva_confirm': 'PasswordDiferente123!'
        }
        
        response = api_client.post(url, datos_cambio, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar mensaje de error
        assert 'password_nueva_confirm' in response.data
        error_message = str(response.data['password_nueva_confirm'])
        assert 'coinciden' in error_message.lower() or 'no coincide' in error_message.lower()
        
        # Validar que la contraseña no se modificó
        usuario_cliente.refresh_from_db()
        assert usuario_cliente.check_password('testpass123')
    
    def test_cambio_password_campos_requeridos(self, api_client, usuario_cliente):
        """
        Prueba que el cambio de contraseña falla cuando faltan campos requeridos.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensajes de error para campos faltantes
        """
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('usuario-cambiar-password', kwargs={'pk': usuario_cliente.id})
        
        # Prueba sin password_actual
        response = api_client.post(url, {
            'password_nueva': 'NuevaPassword123!',
            'password_nueva_confirm': 'NuevaPassword123!'
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_actual' in response.data
        
        # Prueba sin password_nueva
        response = api_client.post(url, {
            'password_actual': 'testpass123',
            'password_nueva_confirm': 'NuevaPassword123!'
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_nueva' in response.data
        
        # Prueba sin password_nueva_confirm
        response = api_client.post(url, {
            'password_actual': 'testpass123',
            'password_nueva': 'NuevaPassword123!'
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_nueva_confirm' in response.data
    
    def test_cambio_password_sin_autenticacion(self, api_client, usuario_cliente):
        """
        Prueba que el cambio de contraseña requiere autenticación.
        
        Valida:
        - Código de respuesta 401 (UNAUTHORIZED)
        """
        url = reverse('usuario-cambiar-password', kwargs={'pk': usuario_cliente.id})
        
        datos_cambio = {
            'password_actual': 'testpass123',
            'password_nueva': 'NuevaPassword123!',
            'password_nueva_confirm': 'NuevaPassword123!'
        }
        
        response = api_client.post(url, datos_cambio, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_cambio_password_otro_usuario_sin_permiso(self, api_client, usuario_cliente, usuario_administrador):
        """
        Prueba que un usuario no puede cambiar la contraseña de otro usuario.
        
        Valida:
        - Código de respuesta 403 (FORBIDDEN) o 404 (NOT FOUND)
        - El usuario solo puede cambiar su propia contraseña (a menos que sea admin)
        """
        # Cliente intenta cambiar contraseña de administrador
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('usuario-cambiar-password', kwargs={'pk': usuario_administrador.id})
        
        datos_cambio = {
            'password_actual': 'adminpass123',
            'password_nueva': 'NuevaPassword123!',
            'password_nueva_confirm': 'NuevaPassword123!'
        }
        
        response = api_client.post(url, datos_cambio, format='json')
        
        # Validar código de respuesta (403 o 404 dependiendo de la implementación)
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
    
    def test_cambio_password_admin_puede_cambiar_otro_usuario(self, api_client, usuario_administrador, usuario_cliente):
        """
        Prueba que un administrador puede cambiar la contraseña de otro usuario.
        
        Nota: El serializer actual valida password_actual contra request.user (el admin),
        no contra el usuario objetivo. Esto significa que el admin necesita proporcionar
        su propia contraseña actual, no la del usuario objetivo.
        
        Valida:
        - Código de respuesta 200 (OK) si el admin proporciona su propia contraseña
        - El administrador tiene permisos para cambiar contraseñas de otros usuarios
        """
        api_client.force_authenticate(user=usuario_administrador)
        url = reverse('usuario-cambiar-password', kwargs={'pk': usuario_cliente.id})
        
        # Nota: El serializer valida contra request.user (admin), no contra el usuario objetivo
        # Por lo tanto, el admin debe proporcionar su propia contraseña actual
        datos_cambio = {
            'password_actual': 'adminpass123',  # Contraseña del admin, no del cliente
            'password_nueva': 'NuevaPasswordAdmin123!',
            'password_nueva_confirm': 'NuevaPasswordAdmin123!'
        }
        
        response = api_client.post(url, datos_cambio, format='json')
        
        # Validar código de respuesta
        # Con la implementación actual, esto debería funcionar si el admin proporciona su propia contraseña
        assert response.status_code == status.HTTP_200_OK
        
        # Validar que la contraseña del cliente se cambió
        usuario_cliente.refresh_from_db()
        assert usuario_cliente.check_password('NuevaPasswordAdmin123!')
    
    def test_cambio_password_validacion_fuerza_contraseña(self, api_client, usuario_cliente):
        """
        Prueba que la nueva contraseña debe cumplir con las validaciones de Django.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST) para contraseñas débiles
        - Mensaje de error apropiado
        """
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('usuario-cambiar-password', kwargs={'pk': usuario_cliente.id})
        
        # Contraseña demasiado corta o débil
        datos_cambio = {
            'password_actual': 'testpass123',
            'password_nueva': '123',
            'password_nueva_confirm': '123'
        }
        
        response = api_client.post(url, datos_cambio, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar mensaje de error
        assert 'password_nueva' in response.data
    
    def test_cambio_password_mismo_usuario_puede_cambiar(self, api_client, usuario_cliente):
        """
        Prueba que un usuario puede cambiar su propia contraseña.
        
        Valida:
        - Código de respuesta 200 (OK)
        - El usuario autenticado puede cambiar su propia contraseña
        """
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('usuario-cambiar-password', kwargs={'pk': usuario_cliente.id})
        
        datos_cambio = {
            'password_actual': 'testpass123',
            'password_nueva': 'MiNuevaPassword123!',
            'password_nueva_confirm': 'MiNuevaPassword123!'
        }
        
        response = api_client.post(url, datos_cambio, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar que la contraseña se cambió
        usuario_cliente.refresh_from_db()
        assert usuario_cliente.check_password('MiNuevaPassword123!')

