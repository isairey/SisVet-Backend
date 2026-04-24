"""
Pruebas unitarias para el CRUD de usuarios (UsuarioViewSet).

Autor: Jeronimo Rodríguez Sepúlveda
Fecha: 2025-11-10

Este módulo contiene las pruebas para los endpoints CRUD de usuarios:
- GET /api/v1/usuarios/ - Listar usuarios
- POST /api/v1/usuarios/ - Crear usuario
- GET /api/v1/usuarios/{id}/ - Obtener detalle de usuario
- PUT/PATCH /api/v1/usuarios/{id}/ - Actualizar usuario
- DELETE /api/v1/usuarios/{id}/ - Eliminar usuario (soft delete)
- GET /api/v1/usuarios/me/ - Obtener información del usuario actual
"""

import pytest
from django.urls import reverse
from rest_framework import status
from usuarios.models import Usuario, Rol, UsuarioRol, Cliente, Veterinario


@pytest.mark.django_db
class TestListarUsuarios:
    """
    Clase de pruebas para el endpoint de listar usuarios.
    """
    
    def test_listar_usuarios_exitoso(self, usuario_autenticado, usuario_cliente, usuario_administrador):
        """
        Prueba que se pueden listar usuarios autenticados.
        
        Valida:
        - Código de respuesta 200 (OK)
        - Estructura correcta de la respuesta
        - Lista de usuarios en la respuesta
        """
        url = reverse('usuario-list')
        
        response = usuario_autenticado.get(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar estructura de la respuesta
        assert 'results' in response.data or isinstance(response.data, list)
        
        # Si hay paginación, los resultados están en 'results'
        usuarios_data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        assert len(usuarios_data) > 0
    
    def test_listar_usuarios_sin_autenticacion(self, api_client):
        """
        Prueba que listar usuarios requiere autenticación.
        
        Valida:
        - Código de respuesta 401 (UNAUTHORIZED)
        """
        url = reverse('usuario-list')
        
        response = api_client.get(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_listar_usuarios_excluye_eliminados(self, usuario_autenticado, usuario_cliente, db):
        """
        Prueba que la lista no incluye usuarios eliminados (soft delete).
        
        Valida:
        - Los usuarios eliminados no aparecen en la lista
        """
        # Crear y eliminar un usuario
        usuario_eliminado = Usuario.objects.create_user(
            username='eliminado_test',
            email='eliminado@test.com',
            password='testpass123',
            nombre='Usuario',
            apellido='Eliminado',
            estado='activo'
        )
        usuario_eliminado.soft_delete()
        
        url = reverse('usuario-list')
        response = usuario_autenticado.get(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar que el usuario eliminado no está en la lista
        usuarios_data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        usuarios_ids = [usuario['id'] for usuario in usuarios_data]
        assert usuario_eliminado.id not in usuarios_ids


@pytest.mark.django_db
class TestObtenerDetalleUsuario:
    """
    Clase de pruebas para el endpoint de obtener detalle de usuario.
    """
    
    def test_obtener_detalle_usuario_exitoso(self, usuario_autenticado, usuario_cliente):
        """
        Prueba que se puede obtener el detalle de un usuario.
        
        Valida:
        - Código de respuesta 200 (OK)
        - Información completa del usuario
        - Perfiles asociados
        """
        url = reverse('usuario-detail', kwargs={'pk': usuario_cliente.id})
        
        response = usuario_autenticado.get(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar estructura de la respuesta
        assert 'id' in response.data
        assert 'username' in response.data
        assert 'email' in response.data
        assert 'nombre' in response.data
        assert 'apellido' in response.data
        assert 'estado' in response.data
        assert 'roles' in response.data
        
        # Validar datos del usuario
        assert response.data['id'] == usuario_cliente.id
        assert response.data['username'] == usuario_cliente.username
    
    def test_obtener_detalle_usuario_no_existe(self, usuario_autenticado):
        """
        Prueba que obtener detalle de usuario inexistente retorna 404.
        
        Valida:
        - Código de respuesta 404 (NOT FOUND)
        """
        url = reverse('usuario-detail', kwargs={'pk': 99999})
        
        response = usuario_autenticado.get(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCrearUsuario:
    """
    Clase de pruebas para el endpoint de crear usuario.
    """
    
    def test_crear_usuario_admin_exitoso(self, usuario_admin_autenticado, rol_cliente, db):
        """
        Prueba que un administrador puede crear un nuevo usuario.
        
        Valida:
        - Código de respuesta 201 (CREATED)
        - Usuario creado correctamente
        - Roles asignados correctamente
        """
        url = reverse('usuario-list')
        datos_usuario = {
            'username': 'nuevo_usuario_crud',
            'email': 'nuevo_crud@test.com',
            'password': 'TestPassword123!',
            'password_confirm': 'TestPassword123!',
            'nombre': 'Nuevo',
            'apellido': 'Usuario',
            'estado': 'activo',
            'roles': ['cliente'],
            'perfil_cliente': {
                'telefono': '1234567890',
                'direccion': 'Dirección de prueba'
            }
        }
        
        response = usuario_admin_autenticado.post(url, datos_usuario, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_201_CREATED
        
        # Validar creación en base de datos
        usuario = Usuario.objects.get(username=datos_usuario['username'])
        assert usuario.email == datos_usuario['email']
        assert usuario.nombre == datos_usuario['nombre']
        assert usuario.apellido == datos_usuario['apellido']
        
        # Validar roles
        assert usuario.usuario_roles.filter(rol__nombre='cliente').exists()
        
        # Validar perfil de cliente
        assert hasattr(usuario, 'perfil_cliente')
        assert usuario.perfil_cliente.telefono == datos_usuario['perfil_cliente']['telefono']
    
    def test_crear_usuario_sin_permisos(self, usuario_autenticado, db):
        """
        Prueba que un usuario sin permisos no puede crear usuarios.
        
        Valida:
        - Código de respuesta 403 (FORBIDDEN)
        """
        url = reverse('usuario-list')
        datos_usuario = {
            'username': 'intento_crear',
            'email': 'intento@test.com',
            'password': 'TestPassword123!',
            'password_confirm': 'TestPassword123!',
            'nombre': 'Intento',
            'apellido': 'Crear',
            'roles': ['cliente']
        }
        
        response = usuario_autenticado.post(url, datos_usuario, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestActualizarUsuario:
    """
    Clase de pruebas para el endpoint de actualizar usuario.
    """
    
    def test_actualizar_usuario_propio_exitoso(self, api_client, usuario_cliente):
        """
        Prueba que un usuario puede actualizar su propia información.
        
        Valida:
        - Código de respuesta 200 (OK)
        - Datos actualizados correctamente
        """
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('usuario-detail', kwargs={'pk': usuario_cliente.id})
        
        datos_actualizacion = {
            'nombre': 'Nombre Actualizado',
            'apellido': 'Apellido Actualizado',
            'email': 'actualizado@test.com'
        }
        
        response = api_client.patch(url, datos_actualizacion, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar actualización en base de datos
        usuario_cliente.refresh_from_db()
        assert usuario_cliente.nombre == datos_actualizacion['nombre']
        assert usuario_cliente.apellido == datos_actualizacion['apellido']
        assert usuario_cliente.email == datos_actualizacion['email']
    
    def test_actualizar_otro_usuario_sin_permisos(self, api_client, usuario_cliente, usuario_administrador):
        """
        Prueba que un usuario no puede actualizar otro usuario sin permisos.
        
        Valida:
        - Código de respuesta 403 (FORBIDDEN) o 404 (NOT FOUND)
        """
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('usuario-detail', kwargs={'pk': usuario_administrador.id})
        
        datos_actualizacion = {
            'nombre': 'Nombre Modificado'
        }
        
        response = api_client.patch(url, datos_actualizacion, format='json')
        
        # Validar código de respuesta
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
    
    def test_actualizar_usuario_admin_puede(self, api_client, usuario_administrador, usuario_cliente):
        """
        Prueba que un administrador puede actualizar cualquier usuario.
        
        Valida:
        - Código de respuesta 200 (OK)
        - Actualización exitosa
        """
        api_client.force_authenticate(user=usuario_administrador)
        url = reverse('usuario-detail', kwargs={'pk': usuario_cliente.id})
        
        datos_actualizacion = {
            'nombre': 'Nombre Modificado por Admin'
        }
        
        response = api_client.patch(url, datos_actualizacion, format='json')
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar actualización
        usuario_cliente.refresh_from_db()
        assert usuario_cliente.nombre == datos_actualizacion['nombre']


@pytest.mark.django_db
class TestEliminarUsuario:
    """
    Clase de pruebas para el endpoint de eliminar usuario (soft delete).
    """
    
    def test_eliminar_usuario_admin_exitoso(self, api_client, usuario_administrador, db):
        """
        Prueba que un administrador puede eliminar un usuario (soft delete).
        
        Valida:
        - Código de respuesta 204 (NO CONTENT)
        - Usuario marcado como eliminado (soft delete)
        - Usuario aún existe en la base de datos
        """
        # Crear usuario para eliminar
        usuario_a_eliminar = Usuario.objects.create_user(
            username='eliminar_test',
            email='eliminar@test.com',
            password='testpass123',
            nombre='Usuario',
            apellido='Eliminar',
            estado='activo'
        )
        
        api_client.force_authenticate(user=usuario_administrador)
        url = reverse('usuario-detail', kwargs={'pk': usuario_a_eliminar.id})
        
        response = api_client.delete(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Validar soft delete
        usuario_a_eliminar.refresh_from_db()
        assert usuario_a_eliminar.deleted_at is not None
        
        # Validar que el usuario aún existe en la BD
        assert Usuario.objects.filter(id=usuario_a_eliminar.id).exists()
    
    def test_eliminar_usuario_sin_permisos(self, api_client, usuario_cliente, usuario_administrador):
        """
        Prueba que un usuario sin permisos no puede eliminar usuarios.
        
        Valida:
        - Código de respuesta 403 (FORBIDDEN)
        """
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('usuario-detail', kwargs={'pk': usuario_administrador.id})
        
        response = api_client.delete(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUsuarioMe:
    """
    Clase de pruebas para el endpoint /usuarios/me/.
    """
    
    def test_obtener_usuario_actual_exitoso(self, api_client, usuario_cliente):
        """
        Prueba que se puede obtener la información del usuario actual.
        
        Valida:
        - Código de respuesta 200 (OK)
        - Información del usuario autenticado
        """
        api_client.force_authenticate(user=usuario_cliente)
        url = reverse('usuario-me')
        
        response = api_client.get(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_200_OK
        
        # Validar datos del usuario
        assert response.data['id'] == usuario_cliente.id
        assert response.data['username'] == usuario_cliente.username
        assert response.data['email'] == usuario_cliente.email
    
    def test_obtener_usuario_actual_sin_autenticacion(self, api_client):
        """
        Prueba que obtener usuario actual requiere autenticación.
        
        Valida:
        - Código de respuesta 401 (UNAUTHORIZED)
        """
        url = reverse('usuario-me')
        
        response = api_client.get(url)
        
        # Validar código de respuesta
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

