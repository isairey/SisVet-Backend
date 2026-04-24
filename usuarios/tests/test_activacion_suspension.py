"""
Pruebas unitarias para los endpoints de activación y suspensión de usuarios.

Autor: Jeronimo Rodríguez Sepúlveda
Fecha: 2025-11-10

Este módulo contiene las pruebas para los endpoints:
- POST /api/v1/usuarios/{id}/activar/ - Activar un usuario
- POST /api/v1/usuarios/{id}/suspender/ - Suspender un usuario
"""

import pytest
from django.urls import reverse
from rest_framework import status
from usuarios.models import Usuario, Rol, UsuarioRol


@pytest.mark.django_db
class TestActivarUsuario:
    """
    Clase de pruebas para el endpoint de activar usuario.
    """
    
    def test_activar_usuario_exitoso(self, api_client, usuario_administrador, db):
        """
        Prueba que un administrador puede activar un usuario suspendido.
        
        Valida:
        - Código de respuesta 200 (OK)
        - Estado del usuario cambia a 'activo'
        - is_active se establece en True
        - Mensaje de éxito en la respuesta
        """
        # Crear usuario suspendido
        usuario_suspendido = Usuario.objects.create_user(
            username='suspendido_activar',
            email='suspendido_activar@test.com',
            password='testpass123',
            nombre='Usuario',
            apellido='Suspendido',
            estado='suspendido',
            is_active=False
        )
        rol_cliente, _ = Rol.objects.get_or_create(nombre='cliente')
        UsuarioRol.objects.create(usuario=usuario_suspendido, rol=rol_cliente)
        
        api_client.force_authenticate(user=usuario_administrador)
        url = reverse('usuario-activar', kwargs={'pk': usuario_suspendido.id})
        
        response = api_client.post(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar mensaje de éxito
        assert 'detail' in response.data
        assert 'activado' in response.data['detail'].lower()
        
        # Validar cambio de estado en base de datos
        usuario_suspendido.refresh_from_db()
        assert usuario_suspendido.estado == 'activo'
        assert usuario_suspendido.is_active is True
    
    def test_activar_usuario_inactivo(self, api_client, usuario_administrador, db):
        """
        Prueba que se puede activar un usuario inactivo.
        
        Valida:
        - Código de respuesta 200 (OK)
        - Estado cambia a 'activo'
        - is_active se establece en True
        """
        # Crear usuario inactivo
        usuario_inactivo = Usuario.objects.create_user(
            username='inactivo_activar',
            email='inactivo_activar@test.com',
            password='testpass123',
            nombre='Usuario',
            apellido='Inactivo',
            estado='inactivo',
            is_active=False
        )
        rol_cliente, _ = Rol.objects.get_or_create(nombre='cliente')
        UsuarioRol.objects.create(usuario=usuario_inactivo, rol=rol_cliente)
        
        api_client.force_authenticate(user=usuario_administrador)
        url = reverse('usuario-activar', kwargs={'pk': usuario_inactivo.id})
        
        response = api_client.post(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar cambio de estado
        usuario_inactivo.refresh_from_db()
        assert usuario_inactivo.estado == 'activo'
        assert usuario_inactivo.is_active is True
    
    def test_activar_usuario_sin_permisos(self, api_client, usuario_cliente, db):
        """
        Prueba que un usuario sin permisos no puede activar usuarios.
        
        Valida:
        - Código de respuesta 403 (FORBIDDEN)
        """
        # Crear usuario suspendido
        usuario_suspendido = Usuario.objects.create_user(
            username='suspendido_test',
            email='suspendido_test@test.com',
            password='testpass123',
            nombre='Usuario',
            apellido='Suspendido',
            estado='suspendido',
            is_active=False
        )
        rol_cliente, _ = Rol.objects.get_or_create(nombre='cliente')
        UsuarioRol.objects.create(usuario=usuario_suspendido, rol=rol_cliente)
        
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('usuario-activar', kwargs={'pk': usuario_suspendido.id})
        
        response = api_client.post(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_activar_usuario_no_existe(self, api_client, usuario_administrador):
        """
        Prueba que activar un usuario inexistente retorna 404.
        
        Valida:
        - Código de respuesta 404 (NOT FOUND)
        """
        api_client.force_authenticate(user=usuario_administrador)
        url = reverse('usuario-activar', kwargs={'pk': 99999})
        
        response = api_client.post(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_activar_usuario_ya_activo(self, api_client, usuario_administrador, usuario_cliente):
        """
        Prueba que activar un usuario ya activo funciona correctamente.
        
        Valida:
        - Código de respuesta 200 (OK)
        - El usuario permanece activo
        """
        api_client.force_authenticate(user=usuario_administrador)
        url = reverse('usuario-activar', kwargs={'pk': usuario_cliente.id})
        
        response = api_client.post(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar que el usuario sigue activo
        usuario_cliente.refresh_from_db()
        assert usuario_cliente.estado == 'activo'
        assert usuario_cliente.is_active is True


@pytest.mark.django_db
class TestSuspenderUsuario:
    """
    Clase de pruebas para el endpoint de suspender usuario.
    """
    
    def test_suspender_usuario_exitoso(self, api_client, usuario_administrador, db):
        """
        Prueba que un administrador puede suspender un usuario.
        
        Valida:
        - Código de respuesta 200 (OK)
        - Estado del usuario cambia a 'suspendido'
        - is_active se establece en False
        - Mensaje de éxito en la respuesta
        """
        # Crear usuario activo
        usuario_activo = Usuario.objects.create_user(
            username='activo_suspender',
            email='activo_suspender@test.com',
            password='testpass123',
            nombre='Usuario',
            apellido='Activo',
            estado='activo',
            is_active=True
        )
        rol_cliente, _ = Rol.objects.get_or_create(nombre='cliente')
        UsuarioRol.objects.create(usuario=usuario_activo, rol=rol_cliente)
        
        api_client.force_authenticate(user=usuario_administrador)
        url = reverse('usuario-suspender', kwargs={'pk': usuario_activo.id})
        
        response = api_client.post(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar mensaje de éxito
        assert 'detail' in response.data
        assert 'suspendido' in response.data['detail'].lower()
        
        # Validar cambio de estado en base de datos
        usuario_activo.refresh_from_db()
        assert usuario_activo.estado == 'suspendido'
        assert usuario_activo.is_active is False
    
    def test_suspender_usuario_sin_permisos(self, api_client, usuario_cliente, db):
        """
        Prueba que un usuario sin permisos no puede suspender usuarios.
        
        Valida:
        - Código de respuesta 403 (FORBIDDEN)
        """
        # Crear usuario activo
        usuario_activo = Usuario.objects.create_user(
            username='activo_test',
            email='activo_test@test.com',
            password='testpass123',
            nombre='Usuario',
            apellido='Activo',
            estado='activo',
            is_active=True
        )
        rol_cliente, _ = Rol.objects.get_or_create(nombre='cliente')
        UsuarioRol.objects.create(usuario=usuario_activo, rol=rol_cliente)
        
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('usuario-suspender', kwargs={'pk': usuario_activo.id})
        
        response = api_client.post(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_suspender_usuario_no_existe(self, api_client, usuario_administrador):
        """
        Prueba que suspender un usuario inexistente retorna 404.
        
        Valida:
        - Código de respuesta 404 (NOT FOUND)
        """
        api_client.force_authenticate(user=usuario_administrador)
        url = reverse('usuario-suspender', kwargs={'pk': 99999})
        
        response = api_client.post(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_suspender_propia_cuenta_bloqueado(self, api_client, usuario_administrador):
        """
        Prueba que un administrador no puede suspender su propia cuenta.
        
        Valida:
        - Código de respuesta 400 (BAD REQUEST)
        - Mensaje de error apropiado
        - El usuario no se suspende
        """
        api_client.force_authenticate(user=usuario_administrador)
        url = reverse('usuario-suspender', kwargs={'pk': usuario_administrador.id})
        
        response = api_client.post(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Validar mensaje de error
        assert 'detail' in response.data
        assert 'propia' in response.data['detail'].lower() or 'no puedes' in response.data['detail'].lower()
        
        # Validar que el usuario no se suspendió
        usuario_administrador.refresh_from_db()
        assert usuario_administrador.estado != 'suspendido'
        assert usuario_administrador.is_active is True
    
    def test_suspender_usuario_ya_suspendido(self, api_client, usuario_administrador, db):
        """
        Prueba que suspender un usuario ya suspendido funciona correctamente.
        
        Valida:
        - Código de respuesta 200 (OK)
        - El usuario permanece suspendido
        """
        # Crear usuario suspendido
        usuario_suspendido = Usuario.objects.create_user(
            username='ya_suspendido',
            email='ya_suspendido@test.com',
            password='testpass123',
            nombre='Usuario',
            apellido='Suspendido',
            estado='suspendido',
            is_active=False
        )
        rol_cliente, _ = Rol.objects.get_or_create(nombre='cliente')
        UsuarioRol.objects.create(usuario=usuario_suspendido, rol=rol_cliente)
        
        api_client.force_authenticate(user=usuario_administrador)
        url = reverse('usuario-suspender', kwargs={'pk': usuario_suspendido.id})
        
        response = api_client.post(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar que el usuario sigue suspendido
        usuario_suspendido.refresh_from_db()
        assert usuario_suspendido.estado == 'suspendido'
        assert usuario_suspendido.is_active is False
    
    def test_suspender_y_activar_flujo_completo(self, api_client, usuario_administrador, db):
        """
        Prueba el flujo completo de suspender y luego activar un usuario.
        
        Valida:
        - Suspensión exitosa
        - Activación exitosa
        - Estado final correcto
        """
        # Crear usuario activo
        usuario = Usuario.objects.create_user(
            username='flujo_completo',
            email='flujo_completo@test.com',
            password='testpass123',
            nombre='Usuario',
            apellido='Flujo',
            estado='activo',
            is_active=True
        )
        rol_cliente, _ = Rol.objects.get_or_create(nombre='cliente')
        UsuarioRol.objects.create(usuario=usuario, rol=rol_cliente)
        
        api_client.force_authenticate(user=usuario_administrador)
        
        # Suspender usuario
        url_suspender = reverse('usuario-suspender', kwargs={'pk': usuario.id})
        response_suspender = api_client.post(url_suspender)
        assert response_suspender.status_code == status.HTTP_200_OK
        
        usuario.refresh_from_db()
        assert usuario.estado == 'suspendido'
        assert usuario.is_active is False
        
        # Activar usuario
        url_activar = reverse('usuario-activar', kwargs={'pk': usuario.id})
        response_activar = api_client.post(url_activar)
        assert response_activar.status_code == status.HTTP_200_OK
        
        usuario.refresh_from_db()
        assert usuario.estado == 'activo'
        assert usuario.is_active is True

